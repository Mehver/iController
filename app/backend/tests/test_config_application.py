# SPDX-License-Identifier: BSD-3-Clause
"""Production feedback/restart contracts with stdlib fakes; no Qt rendering claim."""
import ast
import asyncio
from dataclasses import FrozenInstanceError
import ipaddress
from pathlib import Path
import socket
import sys
import types
import unittest
from unittest.mock import Mock, mock_open, patch

from tests.test_brightness_modes import BACKEND, QtFakes, config_module, load, stub


class Signal:
    def __init__(self):
        self.slots = []
    def connect(self, callback):
        self.slots.append(callback)
    def emit(self, *args):
        for callback in list(self.slots):
            callback(*args)


def settings_namespace(config, tr=lambda zh, en: en):
    tree = ast.parse((BACKEND / 'HostDesktopGUI/settings_page.py').read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SettingsPage')
    body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name not in
            ('__init__', '_build_ui', '_make_ip_list_edit', '_tr_reg', '_set_invalid')]
    for node in body:
        node.decorator_list = []
    parse = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_ip_list')
    hosts = ast.parse((BACKEND / 'HostDesktopGUI/main_page.py').read_text())
    host_helpers = [n for n in hosts.body if isinstance(n, ast.FunctionDef) and n.name in ('is_valid_ipv4', 'is_valid_bind_host')]
    ns = dict(Config=config, tr=tr, ipaddress=ipaddress, QMessageBox=Mock(), QPlainTextEdit=object,
              i18n=stub(LANG_ZH='zh', LANG_EN='en', system_language=lambda: 'zh'),
              gui_config=stub(THEME_LIGHT='light', THEME_DARK='dark', system_theme=lambda: 'light'))
    exec(compile(ast.Module(body=[parse, *host_helpers, *body], type_ignores=[]), 'settings_contract', 'exec'), ns)
    return ns


def attach_feedback(page, config, case=None):
    """Bind real feedback methods to existing brightness-test peers."""
    ns = settings_namespace(config)
    names = ('_form_signature', '_connect_form_edits', '_on_form_edited', '_begin_operation',
             '_current_operation', '_render_feedback', '_operation_failed', '_log_application_errors', '_config_bind', '_request_application',
             'resolve_service', 'application_error', 'on_brightness_mode_applied')
    for name in names:
        setattr(page, name, types.MethodType(ns[name], page))
    page._operation_id = page._dirty_revision = 0
    page._operation = None
    page._form_loading = False
    page._form_values = None
    page._pending_brightness_generation = page._failed_brightness_generation = None
    page.port_spin.value.return_value = 3030
    page.host_edit.text.return_value = '0.0.0.0'
    page.apply_requested = Signal()
    page.apply_requested.connect(lambda request: page.resolve_service(request['operation']))
    if case is not None:
        logger = patch.dict(sys.modules, {'HostCore.infra.files.log_manager': stub(LogManager=stub(log_console=Mock()))})
        logger.start()
        case.addCleanup(logger.stop)


class Field:
    def __init__(self, value='', data=None):
        self.raw, self.data, self.tooltip = value, data, ''
        for name in ('activated', 'clicked', 'valueChanged', 'textEdited', 'textChanged'):
            setattr(self, name, Signal())
    def value(self): return self.raw
    def text(self): return str(self.raw)
    def toPlainText(self): return str(self.raw)
    def isChecked(self): return bool(self.raw)
    def currentIndex(self): return int(self.raw)
    def currentData(self): return self.data[self.raw] if self.data else self.raw
    def findData(self, data): return self.data.index(data)
    def setValue(self, value): self.raw = value; self.valueChanged.emit(value)
    def setText(self, value): self.raw = value; self.textChanged.emit()
    def setPlainText(self, value): self.setText(value)
    def setChecked(self, value): self.raw = value
    def setCurrentIndex(self, value): self.raw = value
    def setItemText(self, *args): pass  # Translation does not alter item data.
    def setEnabled(self, value): pass
    def setToolTip(self, value): self.tooltip = value
    def setAccessibleDescription(self, value): pass
    def edit(self, value, signal='valueChanged'):
        self.raw = value
        getattr(self, signal).emit(value)


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.yaml = stub(safe_dump=Mock())
        self.config = config_module(self.yaml).Config
        self.language = ['zh']
        ns = settings_namespace(self.config, lambda zh, en: zh if self.language[0] == 'zh' else en)
        self.ns, self.page = ns, stub()
        p = self.page
        for name, fn in ns.items():
            selected = name.startswith('_') or name in (
                'save', 'reload_from_file', 'load_from_config', 'retranslate',
                'on_brightness_mode_applied', 'resolve_service', 'application_error')
            if selected and callable(fn):
                if getattr(fn, '__code__', None) and fn.__code__.co_filename == 'settings_contract':
                    setattr(p, name, types.MethodType(fn, p))
        values = dict(lang_follow=True, theme_follow=True, tpad_sensitivity=1, mwheel_sensitivity=1,
                      mwheel_constant=0, host_edit='0.0.0.0', port_spin=3030, blacklist_edit='',
                      whitelist_edit='127.0.0.1', log_action=True, log_ips=True,
                      log_connection=False, log_keyboard=False, hint_label='', brightness_description='')
        for name, value in values.items(): setattr(p, name, Field(value))
        for name, data in (('lang_combo', ['zh', 'en']), ('theme_combo', ['light', 'dark']),
                           ('brightness_mode', [0, 1, 2]), ('ip_mode', ['blacklist', 'whitelist'])):
            setattr(p, name, Field(0, data))
        p.saved, p.apply_requested, p.brightness_mode_changed = Signal(), Signal(), Signal()
        p._tr_widgets = []
        p._operation_id = p._dirty_revision = 0
        p._operation = None
        p._form_loading = False
        p._pending_brightness_generation = p._failed_brightness_generation = None
        p._set_invalid = lambda *args: None
        p.load_from_config()
        p._connect_form_edits()
        p.apply_requested.connect(lambda request: p.resolve_service(request['operation']))
        self.application_log = Mock()
        logs = patch.dict(sys.modules, {'HostCore.infra.files.log_manager': stub(LogManager=stub(log_console=self.application_log))})
        logs.start(); self.addCleanup(logs.stop)

    def save(self):
        with patch('builtins.open', mock_open()), patch('builtins.print'):
            self.page.save()

    def test_plain_save_and_reload_have_distinct_success_and_both_notify(self):
        observed = Mock(); self.page.saved.connect(observed)
        self.save()
        self.assertEqual(self.page.hint_label.text(), '配置保存成功，无需重启应用')
        self.config.init = Mock()
        self.page.reload_from_file()
        self.assertEqual(self.page.hint_label.text(), '配置重新加载成功，无需重启应用')
        self.assertEqual(observed.call_count, 2)

    def test_validation_write_and_read_failure_replace_old_success(self):
        self.save()
        self.page.host_edit.edit('invalid', 'textEdited')
        self.save()
        self.assertIn('保存失败', self.page.hint_label.text())
        self.assertTrue(self.page.hint_label.tooltip)
        self.ns['QMessageBox'].warning.assert_called_once()
        self.page.host_edit.edit('localhost', 'textEdited')
        self.yaml.safe_dump.side_effect = OSError('disk full')
        self.save()
        self.assertIn('disk full', self.page.hint_label.tooltip)
        self.config.init = Mock(side_effect=OSError('read denied'))
        self.page.reload_from_file()
        self.assertIn('重新加载失败', self.page.hint_label.text())
        self.assertIn('read denied', self.page.hint_label.tooltip)

    def test_edit_clears_but_focus_program_fill_and_retranslate_preserve(self):
        self.save(); success = self.page.hint_label.text()
        self.page._on_form_edited()  # Focus / same value does not change the signature.
        self.page.load_from_config()
        self.page.retranslate()
        self.assertEqual(self.page.hint_label.text(), success)
        self.page.port_spin.edit(4040)
        self.assertEqual((self.page.hint_label.text(), self.page.hint_label.tooltip), ('', ''))
        self.page.resolve_service(1, 'late bind failure')
        self.assertEqual(self.page.hint_label.text(), '')

    def test_language_save_survives_synchronous_prefs_retranslation(self):
        self.page.lang_follow.edit(False, 'clicked')
        self.page.lang_combo.edit(1, 'activated')
        def prefs():
            self.language[0] = self.config.Gui.LANGUAGE
            self.page.retranslate()
        self.page.saved.connect(prefs)
        self.save()
        self.assertEqual(self.page.hint_label.text(), 'Configuration saved; no application restart required')

    def test_two_async_parts_wait_and_dirty_or_old_operations_cannot_restore_hint(self):
        requests = []
        self.page.apply_requested.slots = [requests.append]
        self.page.brightness_mode.edit(2, 'activated')
        self.save()
        first = requests[-1]['operation']; generation = self.config.Brightness.committed()[0]
        self.assertIn('正在应用', self.page.hint_label.text())
        self.page.resolve_service(first)
        self.assertIn('正在应用', self.page.hint_label.text())
        self.page.on_brightness_mode_applied(generation, 'restore failed')
        self.assertIn('需要重启应用', self.page.hint_label.text())
        self.page.port_spin.edit(4040)
        self.page.on_brightness_mode_applied(generation, None)
        self.assertEqual(self.page.hint_label.text(), '')
        self.save(); latest = requests[-1]['operation']
        self.page.resolve_service(first, 'obsolete result')
        self.assertIn('正在应用', self.page.hint_label.text())
        self.page.resolve_service(latest, 'address in use; old listener restored')
        self.assertIn('服务应用失败', self.page.hint_label.text())
        self.assertIn('old listener restored', self.page.hint_label.tooltip)

    def test_new_save_inherits_inflight_brightness_without_reapplying_it(self):
        requests = []
        self.page.apply_requested.slots = [requests.append]
        modes = Mock(); self.page.brightness_mode_changed.connect(modes)
        self.page.brightness_mode.edit(2, 'activated'); self.save()
        first = requests[-1]['operation']; generation = self.config.Brightness.committed()[0]
        self.page.log_action.edit(False, 'clicked'); self.save()
        latest = requests[-1]['operation']
        modes.assert_called_once_with(2)
        self.page.resolve_service(first, 'obsolete failure')
        self.page.on_brightness_mode_applied(generation, None)
        self.assertIn('正在应用', self.page.hint_label.text())  # Still waiting for latest service result.
        self.page.resolve_service(latest)
        self.assertEqual(self.page.hint_label.text(), '配置保存成功，无需重启应用')

    def test_unsupported_brightness_does_not_claim_restart_will_add_support(self):
        self.page.brightness_mode.edit(1, 'activated'); self.save()
        generation = self.config.Brightness.committed()[0]
        self.page.on_brightness_mode_applied(generation, dict(message='platform unsupported', restart=False))
        self.assertIn('运行应用失败', self.page.hint_label.text())
        self.assertNotIn('需要重启', self.page.hint_label.text())
        self.assertIn('platform unsupported', self.page.hint_label.tooltip)

    def test_combined_service_and_brightness_failure_retains_restart_requirement_and_all_errors(self):
        self.page.apply_requested.slots = []
        self.page.brightness_mode.edit(2, 'activated'); self.save()
        op = self.page._operation['id']; generation = self.config.Brightness.committed()[0]
        self.page.resolve_service(op, 'address in use; old listener restored')
        self.page.on_brightness_mode_applied(generation, 'Gamma restore failed')
        self.assertIn('保存成功', self.page.hint_label.text())
        self.assertIn('服务应用失败', self.page.hint_label.text())
        self.assertIn('需要重启应用', self.page.hint_label.text())
        for error in ('address in use', 'Gamma restore failed'):
            self.assertIn(error, self.page.hint_label.tooltip)
            self.assertIn(error, self.application_log.call_args.args[0])

    def test_reload_loop_close_failure_requires_restart_but_binding_error_alone_does_not(self):
        self.config.init = Mock(); self.page.apply_requested.slots = []
        self.page.reload_from_file()
        self.page.resolve_service(self.page._operation['id'], dict(message='event loop close failed', restart=True))
        self.assertIn('重新加载成功', self.page.hint_label.text())
        self.assertIn('需要重启应用', self.page.hint_label.text())
        self.save()
        self.page.resolve_service(self.page._operation['id'], 'port occupied')
        self.assertIn('服务应用失败', self.page.hint_label.text())
        self.assertNotIn('需要重启应用', self.page.hint_label.text())

    def test_reload_published_generation_is_retried_after_fill_or_validation_failure(self):
        for failure in ('fill', 'validation'):
            with self.subTest(failure=failure):
                self.config.Brightness.MODE = 0
                self.page.brightness_mode.setCurrentIndex(0)
                self.config.HttpServer.PORT = 3030
                original_fill = self.page._fill_from_config
                def init():
                    self.config.Brightness.MODE = 2
                    if failure == 'validation': self.config.HttpServer.PORT = 0
                def broken_fill():
                    self.page.brightness_mode.setCurrentIndex(2)
                    raise ValueError('fill failed after MODE publication')
                self.config.init = init
                if failure == 'fill': self.page._fill_from_config = broken_fill
                try:
                    self.page.reload_from_file()
                finally:
                    self.page._fill_from_config = original_fill
                generation = self.config.Brightness.committed()[0]
                self.assertEqual(self.page._failed_brightness_generation, generation)
                self.assertIn('重新加载失败', self.page.hint_label.text())
                self.page.port_spin.setValue(3030)
                modes = Mock(); self.page.brightness_mode_changed.slots = [modes]
                self.save()  # MODE is already 2; the generation still needs application.
                modes.assert_called_once_with(2)
                self.assertTrue(self.page._operation['brightness'])
                self.page.on_brightness_mode_applied(generation, None)
                self.assertIn('无需重启应用', self.page.hint_label.text())
                self.save()  # Confirmed generation: unrelated save must not reset/reapply it.
                modes.assert_called_once_with(2)

    def test_main_window_application_slot_requests_restart_only_for_changed_config_bind(self):
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        apply = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_apply_configuration')
        ns = {}; exec(compile(ast.Module(body=[apply], type_ignores=[]), 'main_apply', 'exec'), ns)
        started, stopped = [], []
        service = ServiceApply(lambda *bind: started.append(bind) or len(started), lambda: stopped.append(True),
                               self.page.resolve_service, lambda text: None)
        service.manual_start('127.0.0.1', 3030)
        service.on_state(stub(request_id=1, phase='running', running=True, error=''))
        owner = stub(main_page=stub(sync_config_bind=Mock()), apply_gui_prefs=Mock(), _service_apply=service,
                     _settings_page=self.page, _application_log=Mock(), _resolve_service=self.page.resolve_service)
        self.page.apply_requested.slots = [lambda request: ns['_apply_configuration'](owner, request)]
        self.page.port_spin.edit(4040); self.save()
        self.assertEqual(stopped, [True]); self.assertEqual(len(started), 1)
        service.on_state(stub(request_id=1, phase='stopped', running=False, error=''))
        self.assertEqual(started[-1], ('0.0.0.0', 4040))
        service.on_state(stub(request_id=2, phase='running', running=True, error=''))
        self.assertIn('无需重启应用', self.page.hint_label.text())
        self.page.log_ips.edit(False, 'clicked'); self.save()
        self.assertEqual(len(started), 2); self.assertEqual(stopped, [True])

    def test_main_panel_config_sync_preserves_custom_choice_and_unsubmitted_port(self):
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_page.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainPage')
        sync = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'sync_config_bind')
        ns = {}; exec(compile(ast.Module(body=[sync], type_ignores=[]), 'panel_sync', 'exec'), ns)
        panel = stub(port_spin=Field(3333), host_mode=Field(3), custom_ip=Field('127.0.0.2'),
                     _refresh_host_mode_texts=Mock(), _validate_all=Mock())
        ns['sync_config_bind'](panel, ('0.0.0.0', 3030), ('localhost', 4040))
        self.assertEqual(panel.port_spin.value(), 3333)
        self.assertEqual(panel.host_mode.currentIndex(), 3)
        self.assertEqual(panel.custom_ip.text(), '127.0.0.2')
        panel.port_spin.setValue(3030)
        ns['sync_config_bind'](panel, ('0.0.0.0', 3030), ('localhost', 4040))
        self.assertEqual(panel.port_spin.value(), 4040)

    def test_finished_operation_crash_updates_real_panel_slot_and_log_without_reviving_hint(self):
        self.save(); results = Mock(wraps=self.page.resolve_service); logs = []
        starts = []
        service = ServiceApply(lambda *bind: starts.append(bind) or len(starts), lambda: None, results, logs.append)
        a, b = ('127.0.0.1', 3030), ('0.0.0.0', 4040)
        service.manual_start(*a)
        service.on_state(stub(request_id=1, phase='running', running=True, error=''))
        service.apply(a, b, self.page._operation['id'])
        service.on_state(stub(request_id=1, phase='stopped', running=False, error=''))
        service.on_state(stub(request_id=2, phase='running', running=True, error=''))
        self.config.HttpServer.PORT = 4040; self.page.load_from_config(); self.save()
        service.apply(b, b, self.page._operation['id'])  # A newer unrelated save has finished too.
        self.page.log_ips.edit(False, 'clicked')
        results.reset_mock()
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_page.py').read_text())
        panel_cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainPage')
        panel_state = next(n for n in panel_cls.body if isinstance(n, ast.FunctionDef) and n.name == 'on_state_changed')
        panel_state.decorator_list = []
        ns = dict(ServerState=object, tr=lambda zh, en: en)
        exec(compile(ast.Module(body=[panel_state], type_ignores=[]), 'panel_health', 'exec'), ns)
        panel = stub(power_button=Mock(), status_label=Mock(), qr_view=Mock(), qr_url_label=Mock(), _validate_all=Mock())
        panel.on_state_changed = types.MethodType(ns['on_state_changed'], panel)
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        on_state = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'on_state_changed')
        on_state.decorator_list = []
        exec(compile(ast.Module(body=[on_state], type_ignores=[]), 'window_health', 'exec'), ns)
        owner = stub(main_page=panel, _really_quit=False, _update_tray_tooltip=Mock(), _service_apply=service)
        failed = stub(request_id=2, phase='stopped', running=False, error='runtime crash', bind='', url='')
        ns['on_state_changed'](owner, failed)
        results.assert_not_called()
        self.assertEqual(self.page.hint_label.text(), '')
        panel.status_label.setText.assert_called_with('Stopped')
        panel.qr_view.clear.assert_called_once()
        self.assertTrue(any('runtime crash' in text for text in logs))


ServiceApply = load('service_apply_test', 'HostDesktopGUI/config_apply.py', {}).ServiceApply


class ServiceTests(unittest.TestCase):
    A, B, C = ('127.0.0.1', 3030), ('0.0.0.0', 4040), ('localhost', 5050)
    def setUp(self):
        self.started, self.results, self.events = [], [], []
        def start(host, port): self.started.append((host, port)); return len(self.started)
        self.service = ServiceApply(start, lambda: self.events.append('stop'),
                                    lambda *args: self.results.append(args), self.events.append)
    def state(self, phase, error=''):
        self.service.on_state(stub(phase=phase, running=phase == 'running', error=error,
                                  request_id=self.service.request_id))
    def running(self):
        self.service.manual_start(*self.A); self.state('starting'); self.state('running')
    def test_stopped_never_starts_and_unrelated_save_preserves_manual_listener(self):
        self.service.apply(self.A, self.B, 1)
        self.assertEqual(self.started, [])
        self.running(); self.service.apply(self.B, self.B, 2)
        self.assertEqual(self.started, [self.A])
        self.assertEqual(self.results[-1], (2, None))
    def test_running_restart_waits_for_stopped_and_trustworthy_running(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.assertEqual(self.started, [self.A])
        self.state('stopped'); self.assertEqual(self.started, [self.A, self.B])
        self.state('starting'); self.assertEqual(self.results, [])
        self.state('running'); self.assertEqual(self.results[-1], (1, None))
    def test_failed_bind_restores_old_once_and_keeps_failure_fact(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.state('stopped'); self.state('stopped', 'port occupied')
        self.assertEqual(self.started, [self.A, self.B, self.A])
        self.state('running')
        self.assertIn('old service restored', self.results[-1][1])
        self.service.apply(self.B, self.B, 2)
        self.assertIn('port occupied', self.results[-1][1])
        self.assertEqual(len(self.started), 3)
    def test_failed_restore_stops_without_infinite_retry(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.state('stopped'); self.state('stopped', 'new bind failed'); self.state('stopped', 'old bind also occupied')
        self.assertFalse(self.service.wanted)
        self.assertEqual(len(self.started), 3)
        self.assertIn('service stopped', self.results[-1][1])
    def test_rapid_saves_merge_latest_even_while_starting(self):
        self.service.manual_start(*self.A)
        self.service.apply(self.A, self.B, 1); self.service.apply(self.B, self.C, 2)
        self.state('stopped'); self.assertEqual(self.started, [self.A, self.C])
        self.service.apply(self.C, self.C, 3)  # Unrelated latest save waits on same restart.
        self.state('running'); self.assertEqual(self.results[-1], (3, None))
    def test_late_ready_of_old_start_is_still_available_for_one_rollback(self):
        self.service.manual_start(*self.A)
        self.service.apply(self.A, self.B, 1)
        self.state('running')  # The old socket really listened before its queued stop.
        self.state('stopped'); self.state('stopped', 'new bind failed')
        self.assertEqual(self.started, [self.A, self.B, self.A])
    def test_start_already_targeting_new_config_is_not_cancelled_and_started_twice(self):
        self.service.manual_start(*self.B)
        self.service.apply(self.A, self.B, 1)
        self.assertEqual(self.events.count('stop'), 0)
        self.state('running')
        self.assertEqual(self.started, [self.B])
        self.assertEqual(self.results[-1], (1, None))
    def test_manual_stop_and_quit_cancel_pending_restart(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.service.manual_stop(); self.state('stopped')
        self.assertEqual(self.started, [self.A])
        self.service.apply(self.B, self.C, 2)
        self.assertEqual(self.started, [self.A])
        self.service.manual_start(*self.C); self.service.apply(self.C, self.B, 3)
        self.service.quit(); self.state('stopped')
        self.assertEqual(self.started, [self.A, self.C])

    def test_a_previous_manual_session_is_not_an_automatic_rollback_target(self):
        self.running(); self.service.manual_stop(); self.state('stopped')
        self.service.manual_start(*self.C)
        self.service.apply(self.C, self.B, 1)
        self.state('stopped'); self.state('stopped', 'new bind failed')
        self.assertEqual(self.started, [self.A, self.C, self.B])
        self.assertFalse(self.service.wanted)
    def test_loop_close_failure_never_queues_another_start(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.state('failed', 'event loop close failed; restart required')
        self.assertEqual(self.started, [self.A])
        self.service.apply(self.B, self.C, 2)
        self.assertEqual(self.started, [self.A])
        self.assertTrue(self.results[-1][1]['restart'])
        self.assertIn('restart required', self.results[-1][1]['message'])

    def test_health_failure_after_ready_never_updates_finished_configuration_operation(self):
        self.running(); self.service.apply(self.A, self.B, 1)
        self.state('stopped'); self.state('running')
        self.service.apply(self.B, self.B, 2)  # Later unrelated operation also finishes.
        self.results.clear()
        self.state('stopped', 'runtime server crash')
        self.assertEqual(self.results, [])
        self.assertTrue(any('runtime server crash' in event for event in self.events))
        self.assertEqual(self.service.phase, 'stopped')


class PowerButtonTests(unittest.TestCase):
    def test_auto_stopping_button_cancels_through_real_slots_and_repeated_clicks_are_idempotent(self):
        panel_tree = ast.parse((BACKEND / 'HostDesktopGUI/main_page.py').read_text())
        cls = next(n for n in panel_tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainPage')
        names = {'_busy_text', '_set_busy', '_update_power_enabled', '_on_power_clicked'}
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
        for method in methods: method.decorator_list = []
        ns = dict(tr=lambda zh, en: en, QMessageBox=Mock(), check_bind=Mock())
        exec(compile(ast.Module(body=methods, type_ignores=[]), 'real_power_methods', 'exec'), ns)
        button = stub(enabled=False, clicked=Signal())
        button.setEnabled = lambda value: setattr(button, 'enabled', value)
        button.click = lambda: button.clicked.emit() if button.enabled else None
        panel = stub(_state=stub(phase='running', running=True), _busy=False, _busy_kind='',
                     _auto_stop_cancellable=False, power_button=button, status_label=Mock(), stop_requested=Signal())
        for name in names: setattr(panel, name, types.MethodType(ns[name], panel))
        button.clicked.connect(panel._on_power_clicked)
        window_tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        window = next(n for n in window_tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        controller_methods = [n for n in window.body if isinstance(n, ast.FunctionDef) and n.name in ('_stop_for_apply', '_on_stop_requested')]
        for method in controller_methods: method.decorator_list = []
        owner_ns = {}; exec(compile(ast.Module(body=controller_methods, type_ignores=[]), 'real_stop_methods', 'exec'), owner_ns)
        owner = stub(main_page=panel, _really_quit=False, worker=stub(stop_server=Mock()))
        for name, fn in owner_ns.items():
            if name in ('_stop_for_apply', '_on_stop_requested'): setattr(owner, name, types.MethodType(fn, owner))
        started = []
        service = ServiceApply(lambda *bind: started.append(bind) or len(started), owner._stop_for_apply, lambda *args: None, lambda text: None)
        owner._service_apply = service
        panel.stop_requested.connect(owner._on_stop_requested)
        service.manual_start('127.0.0.1', 3030)
        service.on_state(stub(request_id=1, phase='running', running=True, error=''))
        service.apply(('127.0.0.1', 3030), ('0.0.0.0', 4040), 1)
        self.assertTrue(button.enabled)
        self.assertTrue(panel._auto_stop_cancellable)
        button.click()
        self.assertFalse(service.wanted)
        self.assertIsNone(service.restart)
        self.assertFalse(button.enabled)
        calls = owner.worker.stop_server.call_count
        button.click(); panel._on_power_clicked()  # Includes an already queued duplicate click.
        self.assertEqual(owner.worker.stop_server.call_count, calls)
        service.on_state(stub(request_id=1, phase='stopped', running=False, error=''))
        self.assertEqual(started, [('127.0.0.1', 3030)])
        panel._set_busy(True, 'stopping')  # Ordinary stopping stays disabled.
        self.assertFalse(button.enabled)


class WorkerTests(unittest.TestCase):
    def test_window_quit_waits_via_finished_signal_not_gui_thread_wait(self):
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        close = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'closeEvent')
        app = Mock(); running = [True]; events = []
        ns = dict(QApplication=stub(instance=lambda: app), QSystemTrayIcon=Mock(), tr=lambda zh, en: en, APP_NAME='iController')
        exec(compile(ast.Module(body=[close], type_ignores=[]), 'window_quit', 'exec'), ns)
        thread = stub(finished=Signal(), isRunning=lambda: running[0], quit=Mock())
        owner = stub(_really_quit=True, _quit_waiting=False, _service_apply=stub(quit=Mock()),
                     _brightness_overlay=None, worker=stub(stop_server=Mock()), thread=thread,
                     tray_icon=Mock(), _application_log=Mock())
        def closing():
            event = Mock(); events.append(event); ns['closeEvent'](owner, event)
        owner.close = closing
        closing()
        events[0].ignore.assert_called_once(); app.quit.assert_not_called()
        running[0] = False; thread.finished.emit()
        events[1].accept.assert_called_once(); app.quit.assert_called_once()
        owner._service_apply.quit.assert_called_once()

    def test_application_quit_cancels_service_restart_intent(self):
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        cancel = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_cancel_restart_on_quit')
        ns = {}; exec(compile(ast.Module(body=[cancel], type_ignores=[]), 'quit_intent', 'exec'), ns)
        owner = stub(_really_quit=False, _service_apply=stub(quit=Mock()))
        ns['_cancel_restart_on_quit'](owner)
        self.assertTrue(owner._really_quit)
        owner._service_apply.quit.assert_called_once()

    def worker(self, serve):
        qt = QtFakes()
        deps = dict(qt.modules)
        deps.update({'hypercorn.config': stub(Config=type('Config', (), {})),
                     'hypercorn.asyncio': stub(serve=serve),
                     'HostCore.http_server': stub(HttpServer=lambda path: object()),
                     'HostCore.utils.pyinstaller_context': stub(PyInstallerContext=lambda: stub(frontend_resource_path=lambda: '.'))})
        module = load('config_worker_test', 'HostDesktopGUI/worker.py', deps)
        return module.ServerWorker(), deps
    def test_bind_failure_never_publishes_running_and_stop_snapshot_is_immutable(self):
        async def fail(*args, **kwargs): raise OSError('address in use')
        worker, deps = self.worker(fail); observed = []
        worker.state_changed.connect(observed.append)
        with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', 3030)
        self.assertFalse(any(state.running for state in observed))
        self.assertIn('address in use', observed[-1].error)
        self.assertIsNone(worker._loop)
        with self.assertRaises(FrozenInstanceError): observed[0].running = True
    def test_queued_start_can_be_cancelled_before_native_setup(self):
        serve = Mock()
        worker, deps = self.worker(serve)
        request = worker.prepare_start(); worker.stop_server()
        with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', 3030, request)
        serve.assert_not_called()
        self.assertEqual(worker.state().phase, 'stopped')
    def test_actual_asyncio_listener_is_ready_before_running_and_loop_closes_before_stopped(self):
        probe = socket.socket(); probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]; probe.close()
        holder = {}
        async def serve(app, config, shutdown_trigger):
            server = await asyncio.start_server(lambda r, w: w.close(), '127.0.0.1', port)
            holder['server'] = server
            await asyncio.sleep(0)
            holder['worker'].stop_server()
            await shutdown_trigger()
        worker, deps = self.worker(serve); holder['worker'] = worker
        observed = []
        def state_changed(state):
            if state.running:
                self.assertTrue(holder['server'].is_serving())
            if state.phase == 'stopped': self.assertIsNone(worker._loop)
            observed.append(state)
        worker.state_changed.connect(state_changed)
        with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', port)
        self.assertEqual([state.phase for state in observed], ['starting', 'running', 'stopped'])

    def test_failure_immediately_after_bind_is_not_announced_as_startup_success(self):
        probe = socket.socket(); probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]; probe.close()
        async def serve(*args, **kwargs):
            await asyncio.start_server(lambda r, w: w.close(), '127.0.0.1', port)
            raise RuntimeError('startup failed immediately after socket creation')
        worker, deps = self.worker(serve); observed = []
        worker.state_changed.connect(observed.append)
        with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', port)
        self.assertFalse(any(state.running for state in observed))
        self.assertIn('startup failed', observed[-1].error)

    def test_actual_occupied_port_never_reports_running(self):
        occupied = socket.socket(); occupied.bind(('127.0.0.1', 0)); occupied.listen(1)
        port = occupied.getsockname()[1]
        async def serve(*args, **kwargs):
            await asyncio.start_server(lambda r, w: w.close(), '127.0.0.1', port)
        worker, deps = self.worker(serve); observed = []
        worker.state_changed.connect(observed.append)
        try:
            with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', port)
        finally:
            occupied.close()
        self.assertFalse(any(state.running for state in observed))
        self.assertTrue(observed[-1].error)

    def test_listener_address_matching_checks_host_family_port_and_rejects_zero(self):
        worker, _ = self.worker(Mock())
        socket_stub = lambda host, port, family=socket.AF_INET: stub(family=family, getsockname=lambda: (host, port))
        server = lambda *socks: stub(is_serving=lambda: True, sockets=socks)
        self.assertTrue(worker._listener_matches(server(socket_stub('0.0.0.0', 3030)), {'0.0.0.0'}, 3030))
        self.assertFalse(worker._listener_matches(server(socket_stub('127.0.0.1', 3030)), {'0.0.0.0'}, 3030))
        self.assertFalse(worker._listener_matches(server(socket_stub('127.0.0.2', 3030)), {'127.0.0.1'}, 3030))
        self.assertFalse(worker._listener_matches(server(socket_stub('127.0.0.1', 4040)), {'127.0.0.1'}, 3030))
        self.assertFalse(worker._listener_matches(server(socket_stub('::1', 3030, socket.AF_INET6)), {'127.0.0.1'}, 3030))
        self.assertIn('127.0.0.1', worker._listener_addresses('localhost', 3030))
        self.assertEqual(worker._listener_addresses('0.0.0.0', 3030), frozenset({'0.0.0.0'}))
        with self.assertRaises(ValueError): worker._listener_addresses('127.0.0.1', 0)

    def test_same_port_wrong_address_never_publishes_running(self):
        probe = socket.socket(); probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]; probe.close()
        async def serve(*args, **kwargs):
            await asyncio.start_server(lambda r, w: w.close(), '127.0.0.1', port)
        worker, deps = self.worker(serve); observed = []
        worker.state_changed.connect(observed.append)
        with patch.dict(sys.modules, deps): worker.start_server('0.0.0.0', port)
        self.assertFalse(any(state.running for state in observed))
        self.assertIn('does not match', observed[-1].error)

    def test_lifespan_background_listener_is_not_the_hypercorn_serve_owner(self):
        probe = socket.socket(); probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]; probe.close()
        holder = {}
        async def serve(app, config, shutdown_trigger):
            created, release = asyncio.Event(), asyncio.Event()
            async def lifespan_listener():
                await asyncio.start_server(lambda r, w: w.close(), '127.0.0.1', port)
                created.set()
                await release.wait()
            task = asyncio.create_task(lifespan_listener())
            await created.wait(); await asyncio.sleep(0)
            holder['worker'].stop_server()
            release.set(); await task
        worker, deps = self.worker(serve); holder['worker'] = worker; observed = []
        worker.state_changed.connect(observed.append)
        with patch.dict(sys.modules, deps): worker.start_server('127.0.0.1', port)
        self.assertFalse(any(state.running for state in observed))

    def test_close_failure_is_explicitly_non_reusable_not_a_stopped_success(self):
        async def serve(*args, **kwargs): raise OSError('startup failed')
        worker, deps = self.worker(serve)
        loop = asyncio.new_event_loop(); close = loop.close
        loop.close = Mock(side_effect=RuntimeError('close rejected'))
        try:
            with patch.dict(sys.modules, deps), patch('asyncio.new_event_loop', return_value=loop):
                worker.start_server('127.0.0.1', 3030)
            self.assertEqual(worker.state().phase, 'failed')
            self.assertIn('application restart required', worker.state().error)
        finally:
            close()


if __name__ == '__main__':
    unittest.main()
