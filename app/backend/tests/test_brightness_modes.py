# SPDX-License-Identifier: BSD-3-Clause
"""Stdlib/fake tests of mode and thread contracts, not real Qt/GDI rendering."""

import ast
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import Mock, mock_open, patch


BACKEND = Path(__file__).resolve().parents[1]


def stub(**values):
    return types.SimpleNamespace(**values)


def load(name, relative, dependencies):
    module = types.ModuleType(name)
    with patch.dict(sys.modules, dependencies):
        exec(compile((BACKEND / relative).read_text(encoding='utf-8'), relative, 'exec'), module.__dict__)
    return module


def config_module(yaml=None):
    return load('mode_config_test', 'HostCore/infra/files/config.py', {'yaml': yaml or stub()})


class NativeHarness(unittest.TestCase):
    def setUp(self):
        self.config = config_module().Config
        self.Unsupported = type('Unsupported', (RuntimeError,), {})
        self.log = Mock()
        self.gamma = stub(get_brightness=Mock(return_value=75), set_brightness=Mock(), restore=Mock(return_value=()))
        self.sbc = stub(get_brightness=Mock(return_value=[42]), set_brightness=Mock())
        self.monitors = stub(get_monitors=Mock(return_value=[]))
        self.dependencies = {
            'HostCore.brightness_controller.base': stub(BaseBrightnessController=object, BrightnessUnsupportedError=self.Unsupported),
            'HostCore.infra.files.log_manager': stub(LogManager=stub(log_console=self.log)),
            'HostCore.infra.files.config': stub(Config=self.config),
            'HostCore.utils.check_platform': stub(get_platform=lambda: 'Windows'),
            'HostCore.brightness_controller.windows_gamma': stub(WindowsGammaBrightness=self.gamma),
            'screen_brightness_control': self.sbc, 'monitorcontrol': self.monitors,
        }
        self.registry = load('mode_registry_test', 'HostCore/brightness_controller/__init__.py', self.dependencies)
        self.dependencies['HostCore.brightness_controller'] = self.registry
        self.native = load('mode_windows_test', 'HostCore/brightness_controller/windows.py', self.dependencies)
        self.controller = self.native.WindowsBrightnessController
        self.registry.get_brightness_controller = lambda: self.controller()
        runtime = patch.dict(sys.modules, self.dependencies)
        runtime.start()
        self.addCleanup(runtime.stop)


class ControllerTests(NativeHarness):
    def test_default_hardware_and_ddc_failure_never_use_gamma(self):
        self.assertEqual(self.controller().get_current_brightness(), 42)
        self.controller().set_brightness(50)
        self.gamma.get_brightness.assert_not_called()
        self.gamma.set_brightness.assert_not_called()
        self.gamma.restore.assert_not_called()
        self.sbc.get_brightness.side_effect = OSError('no backlight')
        self.sbc.set_brightness.side_effect = OSError('no backlight')
        for operation in (self.controller().get_current_brightness, lambda: self.controller().set_brightness(50)):
            with self.assertRaises(self.Unsupported):
                operation()
        self.gamma.get_brightness.assert_not_called()
        self.gamma.set_brightness.assert_not_called()

    def test_hardware_still_uses_ddc_and_updates_each_available_monitor(self):
        monitor = Mock()
        monitor.__enter__, monitor.__exit__ = Mock(return_value=monitor), Mock(return_value=False)
        monitor.get_luminance.return_value = 63
        self.monitors.get_monitors.return_value = [monitor]
        self.sbc.get_brightness.side_effect = OSError('SBC unavailable')
        self.sbc.set_brightness.side_effect = OSError('SBC unavailable')
        self.assertEqual(self.controller().get_current_brightness(), 63)
        self.controller().set_brightness(55)
        monitor.set_luminance.assert_called_once_with(55)

    def test_gamma_is_direct_and_preserves_0_100_clamp(self):
        self.config.Brightness.MODE = 2
        self.assertEqual(self.controller().get_current_brightness(), 75)
        self.controller().set_brightness(-10)
        self.controller().set_brightness(120)
        self.assertEqual([c.args[0] for c in self.gamma.set_brightness.call_args_list], [0, 100])
        self.sbc.get_brightness.assert_not_called()
        self.sbc.set_brightness.assert_not_called()
        self.monitors.get_monitors.assert_not_called()

    def test_cli_overlay_is_explicitly_unsupported_no_fallback(self):
        self.config.Brightness.MODE = 1
        for operation in (self.controller().get_current_brightness, lambda: self.controller().set_brightness(50)):
            with self.assertRaises(self.Unsupported):
                operation()
        self.sbc.get_brightness.assert_not_called()
        self.gamma.get_brightness.assert_not_called()
        self.assertTrue(any('requires the desktop GUI' in c.args[0] for c in self.log.call_args_list))

    def test_gamma_cleanup_failure_blocks_new_mode_and_can_retry(self):
        self.config.Brightness.MODE = 2
        self.controller().set_brightness(20)
        self.gamma.restore.return_value = ('display1',)
        self.config.Brightness.MODE = 0
        with self.assertRaises(self.Unsupported):
            self.controller().set_brightness(80)
        self.assertEqual(self.controller._active_mode, 2)
        self.sbc.set_brightness.assert_not_called()
        self.gamma.restore.return_value = ()
        self.controller().set_brightness(80)
        self.sbc.set_brightness.assert_called_once_with(80, no_return=False)

    def test_overlay_cleanup_failure_blocks_gamma_and_unregister_needs_confirmation(self):
        bridge = stub(call=Mock(return_value=100))
        self.registry.register_overlay_bridge(bridge)
        self.config.Brightness.MODE = 1
        self.assertEqual(self.controller().get_current_brightness(), 100)
        bridge.call.side_effect = RuntimeError('clear timed out')
        self.config.Brightness.MODE = 2
        with self.assertRaises(self.Unsupported):
            self.controller().get_current_brightness()
        self.gamma.get_brightness.assert_not_called()
        self.assertEqual(self.controller._active_mode, 1)
        self.registry.unregister_overlay_bridge(bridge, cleared=False)
        with self.assertRaises(self.Unsupported):
            self.controller().get_current_brightness()

    def test_gamma_is_restored_before_overlay_can_set_a_target(self):
        self.config.Brightness.MODE = 2
        self.controller().set_brightness(20)
        events = []
        self.gamma.restore.side_effect = lambda: events.append('gamma cleared') or ()
        bridge = stub(call=lambda kind, value=None: events.append('overlay ' + kind) or value)
        self.registry.register_overlay_bridge(bridge)
        self.config.Brightness.MODE = 1
        self.controller().set_brightness(50)
        self.assertEqual(events, ['gamma cleared', 'overlay set'])
        self.sbc.set_brightness.assert_not_called()

    def test_invalid_direct_mode_rejected_before_native_io(self):
        for mode in (True, False, None, '1', 1.0, -1, 3):
            with self.assertRaises(ValueError):
                self.config.Brightness.MODE = mode
        self.sbc.get_brightness.assert_not_called()
        self.gamma.get_brightness.assert_not_called()


class ConfigTests(unittest.TestCase):
    def test_missing_key_defaults_to_zero_and_saves_number(self):
        yaml = stub(safe_load=Mock(return_value={}), safe_dump=Mock())
        config = config_module(yaml).Config
        config.Brightness.MODE = 2
        with patch('builtins.open', mock_open()), patch('os.path.exists', return_value=True):
            config.init()
        self.assertEqual(config.Brightness.MODE, 0)
        self.assertEqual(yaml.safe_dump.call_args.args[0]['Brightness'], {'MODE': 0})
        self.assertIs(type(yaml.safe_dump.call_args.args[0]['Brightness']['MODE']), int)

    def test_invalid_modes_in_file_or_save_never_publish(self):
        yaml = stub(safe_load=Mock(), safe_dump=Mock())
        config = config_module(yaml).Config
        config.Brightness.MODE = 2
        for value in (True, False, None, '0', 0.0, -1, 3, [], {}):
            yaml.safe_load.return_value = {'Brightness': {'MODE': value}}
            with patch('builtins.open', mock_open()), patch('os.path.exists', return_value=True):
                with self.assertRaises(ValueError):
                    config.init()
                with self.assertRaises(ValueError):
                    config.save(brightness_mode=value)
            self.assertEqual(config.Brightness.MODE, 2)
        yaml.safe_dump.assert_not_called()

    def test_save_failure_and_reload_failure_keep_old_mode(self):
        yaml = stub(safe_load=Mock(return_value={}), safe_dump=Mock(side_effect=OSError('disk full')))
        config = config_module(yaml).Config
        config.Brightness.MODE = 1
        committed = config.Brightness.committed()
        with patch('builtins.open', mock_open()), patch('os.path.exists', return_value=True):
            with self.assertRaises(OSError):
                config.save(brightness_mode=2)
            with self.assertRaises(OSError):
                config.init()
        self.assertEqual(config.Brightness.MODE, 1)
        self.assertIs(config.Brightness.committed(), committed)

    def test_reload_does_not_publish_a_temporary_default(self):
        entered, release = threading.Event(), threading.Event()
        def parse(stream):
            entered.set()
            if not release.wait(2):
                raise TimeoutError('test barrier')
            return {'Brightness': {'MODE': 1}}
        yaml = stub(safe_load=parse, safe_dump=Mock())
        config = config_module(yaml).Config
        config.Brightness.MODE = 2
        with patch('builtins.open', mock_open()), patch('os.path.exists', return_value=True), ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(config.init)
            try:
                self.assertTrue(entered.wait(1))
                self.assertEqual(config.Brightness.MODE, 2)
            finally:
                release.set()
            future.result(timeout=2)
        self.assertEqual(config.Brightness.MODE, 1)

    def test_settings_only_emits_hot_apply_for_a_successful_mode_change(self):
        config = config_module().Config
        def save(*, brightness_mode):
            config.Brightness.MODE = config.Brightness.validate_mode(brightness_mode)
        config.save = Mock(side_effect=save)
        tree = ast.parse((BACKEND / 'HostDesktopGUI/settings_page.py').read_text())
        settings = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SettingsPage')
        function = next(n for n in settings.body if isinstance(n, ast.FunctionDef) and n.name == 'save')
        function.decorator_list = []
        namespace = {'Config': config, 'QMessageBox': Mock(), 'tr': lambda zh, en: en,
                     'parse_ip_list': lambda text: ([], None)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'settings_save', 'exec'), namespace)
        page = Mock()
        page._collect_errors.return_value = []
        page.brightness_mode.currentData.return_value = 0
        with patch('builtins.print'):
            namespace['save'](page)
            page.brightness_mode_changed.emit.assert_not_called()
            page.brightness_mode.currentData.return_value = 1
            namespace['save'](page)
            page.brightness_mode_changed.emit.assert_called_once_with(1)
            namespace['save'](page)
            page.brightness_mode_changed.emit.assert_called_once_with(1)
            config.save.side_effect = OSError('cannot write')
            page.brightness_mode.currentData.return_value = 2
            namespace['save'](page)
        self.assertEqual(config.Brightness.MODE, 1)
        page.brightness_mode_changed.emit.assert_called_once_with(1)

    def test_original_gamma_mapping_and_restore_failure_reporting(self):
        log = Mock()
        gamma = load('mode_gamma_test', 'HostCore/brightness_controller/windows_gamma.py',
                     {'HostCore.infra.files.log_manager': stub(LogManager=stub(log_console=log))})
        ramp = (tuple(i * 257 for i in range(256)),) * 3
        self.assertEqual(gamma._scaled_ramp(ramp, 100), ramp)
        self.assertEqual(gamma._scaled_ramp(ramp, 0)[0][100], round(ramp[0][100] * .5))
        adapter = gamma.WindowsGammaBrightness
        adapter._api = stub(set_gamma_ramp=Mock(side_effect=OSError('disconnected')))
        adapter._baselines = {'active': ramp, 'inactive': ramp}
        adapter._modified_sources = {'active'}
        adapter._current_percent = 20
        with patch.dict(sys.modules, {'HostCore.infra.files.log_manager': stub(LogManager=stub(log_console=log))}):
            self.assertEqual(adapter.restore(), ('active',))
        self.assertEqual(adapter._modified_sources, {'active'})
        self.assertEqual(adapter._current_percent, 20)
        log.assert_called_once()
        adapter._api.set_gamma_ramp.reset_mock(side_effect=True)
        self.assertEqual(adapter.restore(), ())
        adapter._api.set_gamma_ramp.assert_called_once_with('active', ramp)
        self.assertEqual(adapter._current_percent, 100)


class QtFakes:
    def __init__(self):
        self.main = threading.get_ident()
        self.events, self.windows = [], []
        self.qobjects, self.effects = [], []
        self.queued = threading.Event()
        self.show_hook = None
        self.geometry_hook = None
        env = self
        names = ('Tool', 'FramelessWindowHint', 'WindowStaysOnTopHint', 'WindowDoesNotAcceptFocus',
                 'WindowTransparentForInput', 'WA_TranslucentBackground', 'WA_TransparentForMouseEvents',
                 'WA_ShowWithoutActivating', 'WA_AcceptTouchEvents', 'NoFocus', 'QueuedConnection')
        self.qt = stub(**{name: 1 << i for i, name in enumerate(names)})
        class BoundSignal:
            def __init__(self):
                self.slots = []
            def connect(self, function, connection=None):
                self.slots.append((function, connection))
            def disconnect(self, function):
                self.slots = [(f, c) for f, c in self.slots if f != function]
            def emit(self, *args):
                for function, connection in list(self.slots):
                    if connection == env.qt.QueuedConnection:
                        env.events.append((function, args))
                        env.queued.set()
                    else:
                        function(*args)
        class Signal:
            def __init__(self, *args):
                pass
            def __set_name__(self, owner, name):
                self.name = name
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                return instance.__dict__.setdefault('_signal_' + self.name, BoundSignal())
        class QObject:
            destroyed = Signal()
            def __init__(self, parent=None):
                self.parent = parent
                env.qobjects.append(self)
            def deleteLater(self):
                self.deleted = True
        class Window:
            def __init__(self, parent, flags):
                self.parent, self.flags = parent, flags
                self.attributes, self.visible, self.deleted = {}, False, False
                self.screen, self.geometry, self.opacity = None, None, 0
                env.windows.append(self)
            def touch(self):
                if threading.get_ident() != env.main:
                    raise AssertionError('QWidget operated outside Qt main thread')
            def setAttribute(self, name, value):
                self.touch(); self.attributes[name] = value
            def setFocusPolicy(self, policy):
                self.touch(); self.focus = policy
            def winId(self):
                self.touch(); return 1
            def windowHandle(self):
                self.touch(); return self
            def setScreen(self, screen):
                self.touch(); self.screen = screen
            def setGeometry(self, geometry):
                self.touch()
                if env.geometry_hook:
                    env.geometry_hook(self)
                self.geometry = geometry
            def setWindowOpacity(self, opacity):
                self.touch(); self.opacity = opacity
                env.effects.append((self, 'opacity', opacity))
            def show(self):
                self.touch(); self.visible = True
                env.effects.append((self, 'show', self.opacity))
                if env.show_hook:
                    env.show_hook()
            def hide(self):
                self.touch(); self.visible = False
            def close(self):
                self.touch(); self.visible = False
            def deleteLater(self):
                self.touch(); self.deleted = True
        class Screen:
            def __init__(self, geometry):
                self.coords = geometry
                self.geometryChanged = BoundSignal()
            def geometry(self):
                return self.coords
        self.Screen = Screen
        self.screens = [Screen((-1920, 0, 1920, 1080)), Screen((0, 0, 2560, 1440))]
        self.app = stub(screens=lambda: list(env.screens), thread=lambda: env.main,
                        screenAdded=BoundSignal(), screenRemoved=BoundSignal(), aboutToQuit=BoundSignal())
        self.modules = {
            'PySide6.QtCore': stub(QObject=QObject, Qt=self.qt, QThread=stub(currentThread=threading.get_ident),
                                  Signal=Signal, Slot=lambda *args: lambda function: function),
            'PySide6.QtGui': stub(QColor=lambda *args: args, QPainter=Mock()),
            'PySide6.QtWidgets': stub(QApplication=stub(instance=lambda: env.app), QWidget=Window),
        }

    def drain(self):
        while self.events:
            function, args = self.events.pop(0)
            function(*args)
        self.queued.clear()


class OverlayTests(NativeHarness):
    def setUp(self):
        super().setUp()
        self.qt = QtFakes()
        dependencies = dict(self.dependencies, **self.qt.modules)
        self.gui = load('overlay_test', 'HostDesktopGUI/brightness_overlay.py', dependencies)
        self.manager = self.gui.BrightnessOverlayManager(object())
        self.addCleanup(self.close_manager)

    def close_manager(self):
        self.manager.shutdown()
        self.manager._executor.shutdown(wait=True)

    def set_from_worker(self, value):
        self.config.Brightness.MODE = 1
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.controller().set_brightness, value)
            self.assertTrue(self.qt.queued.wait(1))
            self.qt.drain()
            future.result(timeout=1)

    def test_startup_get_100_without_creating_or_showing_windows(self):
        self.config.Brightness.MODE = 1
        self.assertEqual(self.controller().get_current_brightness(), 100)
        self.assertEqual(self.qt.windows, [])
        self.assertEqual(self.qt.events, [])

    def test_per_screen_coordinates_flags_safety_opacity_and_hidden_100(self):
        self.set_from_worker(0)
        self.assertEqual(len(self.manager._windows), 2)
        qt = self.qt.qt
        for screen, window in self.manager._windows.items():
            self.assertIsNone(window.parent)
            self.assertIs(window.screen, screen)
            self.assertEqual(window.geometry, screen.geometry())
            self.assertAlmostEqual(window.opacity, .9)
            for flag in (qt.Tool, qt.FramelessWindowHint, qt.WindowStaysOnTopHint, qt.WindowDoesNotAcceptFocus, qt.WindowTransparentForInput):
                self.assertTrue(window.flags & flag)
            self.assertTrue(window.attributes[qt.WA_ShowWithoutActivating])
            self.assertTrue(window.attributes[qt.WA_TransparentForMouseEvents])
            self.assertFalse(window.attributes[qt.WA_AcceptTouchEvents])
        self.assertEqual(self.controller().get_current_brightness(), 0)
        self.set_from_worker(50)
        self.assertTrue(all(w.opacity == .45 for w in self.qt.windows))
        self.set_from_worker(100)
        self.assertTrue(all(not w.visible for w in self.qt.windows))

    def test_screen_add_remove_and_geometry_changes_keep_each_screen_binding(self):
        self.set_from_worker(50)
        screen = self.qt.screens[0]
        screen.coords = (-2560, -200, 2560, 1440)
        screen.geometryChanged.emit(screen.coords)
        self.assertEqual(self.manager._windows[screen].geometry, screen.coords)
        new_screen = self.qt.Screen((2560, 0, 1920, 1080))
        self.qt.screens.append(new_screen)
        self.qt.app.screenAdded.emit(new_screen)
        self.assertIs(self.manager._windows[new_screen].screen, new_screen)
        self.assertEqual(self.manager._windows[new_screen].opacity, .45)
        window = self.manager._windows[screen]
        self.qt.screens.remove(screen)
        self.qt.app.screenRemoved.emit(screen)
        self.assertTrue(window.deleted)
        self.assertNotIn(screen, self.manager._windows)
        self.assertEqual(screen.geometryChanged.slots, [])

    def test_main_thread_bridge_call_is_direct_no_wait_or_queue(self):
        self.assertEqual(self.manager.bridge.call('set', 50), 50)
        self.assertEqual(self.manager.bridge.call('get'), 50)
        self.assertEqual(self.qt.events, [])
        self.assertEqual(self.manager.bridge.call('clear'), 100)

    def test_worker_cannot_bypass_qt_thread_guard(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.manager._perform, 'set', 50)
            with self.assertRaisesRegex(RuntimeError, 'Qt main thread'):
                future.result(timeout=1)
        self.assertEqual(self.qt.windows, [])

    def test_hot_apply_clears_overlay_in_qt_then_enters_gamma_in_worker(self):
        self.set_from_worker(50)
        self.config.Brightness.MODE = 2
        self.manager.apply_mode(2)
        self.assertTrue(self.qt.queued.wait(1))
        self.qt.drain()
        self.manager._jobs[-1].result(timeout=1)
        self.assertEqual(self.controller._active_mode, 2)
        self.assertTrue(all(not window.visible for window in self.qt.windows))
        self.assertEqual(self.manager.bridge.call('get'), 100)
        self.gamma.get_brightness.assert_not_called()  # Selecting a mode alone adds no effect.
        with ThreadPoolExecutor(max_workers=1) as executor:
            self.assertEqual(executor.submit(self.controller().get_current_brightness).result(timeout=1), 75)

    def test_committed_a_b_a_clears_once_even_when_both_tasks_wait_for_native_lock(self):
        self.config.Brightness.MODE = 2
        self.controller().set_brightness(20)
        self.gamma.restore.reset_mock()
        generation = self.config.Brightness.committed()[0]
        self.config.save.__globals__['yaml'] = stub(safe_dump=Mock())
        self.controller._mode_lock.acquire()
        try:
            with patch('builtins.open', mock_open()):
                self.config.save(brightness_mode=0)
                self.manager.apply_mode(0)
                self.config.save(brightness_mode=2)
                self.manager.apply_mode(2)
                self.config.save(brightness_mode=2)  # Unchanged save adds no generation.
            self.assertEqual(self.config.Brightness.committed(), (generation + 2, 2))
            self.gamma.restore.assert_not_called()
        finally:
            self.controller._mode_lock.release()
        for job in self.manager._jobs:
            job.result(timeout=1)
        self.gamma.restore.assert_called_once_with()
        self.assertEqual(self.controller._applied_generation, generation + 2)

    def test_new_commit_during_overlay_clear_never_dispatches_the_stale_mode(self):
        self.set_from_worker(50)
        self.config.Brightness.MODE = 2
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.controller().get_current_brightness)
            self.assertTrue(self.qt.queued.wait(1))  # Backend is waiting for overlay clear.
            self.config.Brightness.MODE = 0
            self.qt.drain()
            self.assertEqual(future.result(timeout=1), 42)
        self.gamma.get_brightness.assert_not_called()
        self.sbc.get_brightness.assert_called_once_with()
        self.assertEqual(self.controller._active_mode, 0)
        self.assertEqual(self.controller._applied_generation, self.config.Brightness.committed()[0])

    def test_qt_hide_failure_rejects_gamma_mode_without_mixing(self):
        self.set_from_worker(50)
        window = next(iter(self.manager._windows.values()))
        hide = window.hide
        window.hide = Mock(side_effect=RuntimeError('hide rejected'))
        try:
            self.config.Brightness.MODE = 2
            self.manager.apply_mode(2)
            self.assertTrue(self.qt.queued.wait(1))
            self.qt.drain()
            self.manager._jobs[-1].result(timeout=1)
            self.assertEqual(self.controller._active_mode, 1)
            self.gamma.get_brightness.assert_not_called()
            self.assertEqual(self.manager.bridge.call('get'), 50)
        finally:
            window.hide = hide

    def test_removed_screen_cleanup_failure_is_not_reported_as_cleared(self):
        self.set_from_worker(50)
        screen = self.qt.screens[0]
        window = self.manager._windows[screen]
        hide = window.hide
        window.hide = Mock(side_effect=RuntimeError('hide rejected'))
        try:
            self.qt.app.screenRemoved.emit(screen)
            self.assertIn(screen, self.manager._windows)
            self.config.Brightness.MODE = 2
            with self.assertRaises(self.Unsupported):
                self.controller().get_current_brightness()
            self.gamma.get_brightness.assert_not_called()
        finally:
            window.hide = hide

    def test_queued_timeout_cancels_uncommitted_effects_without_invoking_callbacks(self):
        self.manager.bridge._timeout = .02
        self.config.Brightness.MODE = 1
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.controller().set_brightness, 20)
            with self.assertRaises(self.Unsupported):
                future.result(timeout=1)
        request = self.qt.events[0][1][0]
        self.assertTrue(request.cancelled)
        self.assertEqual(request.committed_effects, 0)
        callback = Mock()
        with self.assertRaisesRegex(RuntimeError, 'not committed'):
            self.manager.bridge.run_effect(request, callback, brightness=True)
        callback.assert_not_called()
        self.assertEqual(request.inflight_effects, 0)
        self.qt.drain()
        self.assertEqual(self.qt.windows, [])
        self.assertEqual(self.manager.bridge.call('get'), 100)

    def test_timeout_during_committed_qt_operation_rolls_back_on_main_thread(self):
        self.manager.bridge._timeout = .02
        self.config.Brightness.MODE = 1
        timed_out = threading.Event()
        self.qt.show_hook = lambda: self.assertTrue(timed_out.wait(1))
        def setter():
            try:
                self.controller().set_brightness(20)
            finally:
                timed_out.set()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(setter)
            self.assertTrue(self.qt.queued.wait(1))
            self.qt.drain()
            with self.assertRaises(self.Unsupported):
                future.result(timeout=1)
        self.assertEqual(self.manager.bridge.call('get'), 100)
        self.assertTrue(all(not w.visible for w in self.qt.windows))

    def test_cancel_before_opacity_and_show_commits_produces_no_brightness_calls(self):
        self.set_from_worker(50)
        self.qt.effects.clear()
        self.manager.bridge._timeout = .02
        timed_out = threading.Event()
        self.qt.geometry_hook = lambda window: self.assertTrue(timed_out.wait(1))
        def setter():
            try:
                self.controller().set_brightness(20)
            finally:
                timed_out.set()
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(setter)
                self.assertTrue(self.qt.queued.wait(1))
                self.qt.drain()  # Metadata call blocks; cancellation precedes opacity/show.
                with self.assertRaises(self.Unsupported):
                    future.result(timeout=1)
        finally:
            self.qt.geometry_hook = None
        self.assertEqual(self.qt.effects, [])  # Observe calls, not just final rollback.
        self.assertEqual(self.manager.bridge.call('get'), 50)

    def test_cancellation_after_show_commit_stops_new_target_on_later_screens(self):
        self.set_from_worker(50)
        self.qt.effects.clear()
        self.manager.bridge._timeout = .02
        timed_out = threading.Event()
        self.qt.show_hook = lambda: self.assertTrue(timed_out.wait(1))
        def setter():
            try:
                self.controller().set_brightness(20)
            finally:
                timed_out.set()
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(setter)
                self.assertTrue(self.qt.queued.wait(1))
                self.qt.drain()
                with self.assertRaises(self.Unsupported):
                    future.result(timeout=1)
        finally:
            self.qt.show_hook = None
        applied_new_opacity = [window for window, kind, value in self.qt.effects if kind == 'opacity' and abs(value - .72) < 1e-9]
        self.assertEqual(applied_new_opacity, [self.qt.windows[0]])
        self.assertEqual(self.manager.bridge.call('get'), 50)

    def test_timeout_after_commit_before_native_call_allows_one_callback_then_rolls_back(self):
        self.set_from_worker(50)
        self.qt.effects.clear()
        bridge = self.manager.bridge
        bridge._timeout = .02
        original_commit = bridge._commit_effect
        timed_out = threading.Event()
        requests, grants, starts = [], [], []
        window = self.qt.windows[0]
        original_opacity = window.setWindowOpacity
        def commit_then_pause(request, *, brightness=False):
            original_commit(request, brightness=brightness)
            if request is not None and brightness and not requests:
                requests.append(request)
                grants.append(request.committed_effects)
                # The real commit method returned and released its lock, but
                # run_effect has not called native Qt yet. Cancellation must
                # still finish on the worker while this Qt thread is paused.
                self.assertEqual(self.qt.effects, [])
                self.assertTrue(timed_out.wait(1))
                self.assertTrue(request.cancelled)
                self.assertEqual(request.inflight_effects, 1)
                self.assertTrue(request.brightness_committed)
        def opacity(value):
            starts.append((value, requests[0].cancelled))
            return original_opacity(value)
        def setter():
            try:
                self.controller().set_brightness(20)
            finally:
                timed_out.set()
        bridge._commit_effect = commit_then_pause
        window.setWindowOpacity = opacity
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(setter)
                self.assertTrue(self.qt.queued.wait(1))
                self.qt.drain()
                with self.assertRaises(self.Unsupported) as failure:
                    future.result(timeout=1)
                self.assertIn('committed operations may complete', str(failure.exception.__cause__))
        finally:
            bridge._commit_effect = original_commit
            window.setWindowOpacity = original_opacity
        self.assertTrue(any(abs(value - .72) < 1e-9 and cancelled for value, cancelled in starts))
        self.assertFalse(any(kind == 'show' and abs(value - .72) < 1e-9 for _, kind, value in self.qt.effects))
        self.assertEqual(requests[0].committed_effects, grants[0])  # No later request commit.
        self.assertEqual(requests[0].inflight_effects, 0)
        self.assertEqual(bridge.call('get'), 50)
        self.assertTrue(all(abs(w.opacity - .45) < 1e-9 for w in self.qt.windows))

    def test_committed_effect_exception_releases_inflight_bookkeeping(self):
        request = self.gui._Request('set', 20)
        callback = Mock(side_effect=RuntimeError('native rejected operation'))
        with self.assertRaisesRegex(RuntimeError, 'native rejected'):
            self.manager.bridge.run_effect(request, callback, brightness=True)
        self.assertEqual(request.committed_effects, 1)
        self.assertEqual(request.inflight_effects, 0)
        self.assertTrue(request.brightness_committed)

    def test_teardown_releases_worker_and_late_calls_do_not_touch_qobjects(self):
        self.config.Brightness.MODE = 1
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.controller().set_brightness, 20)
            self.assertTrue(self.qt.queued.wait(1))
            self.manager.shutdown()
            with self.assertRaises(self.Unsupported):
                future.result(timeout=1)
        self.qt.drain()
        with self.assertRaises(RuntimeError):
            self.manager.bridge.call('set', 20)
        self.assertIsNone(self.manager.bridge._post)
        self.assertIsNone(self.registry.overlay_state()[0])
        self.assertTrue(self.registry.overlay_state()[1])
        self.assertEqual(self.qt.windows, [])

    def test_shutdown_does_not_wait_for_native_mode_lock_on_main_thread(self):
        self.controller._mode_lock.acquire()
        try:
            self.manager.shutdown()  # Would deadlock here if it waited for native IO.
            self.assertTrue(self.manager._closed)
        finally:
            self.controller._mode_lock.release()

    def test_unexpected_manager_destruction_cancels_bridge_and_hides_windows(self):
        self.set_from_worker(50)
        self.manager.destroyed.emit()
        with self.assertRaises(RuntimeError):
            self.manager.bridge.call('set', 20)
        self.assertTrue(all(w.deleted and not w.visible for w in self.qt.windows))
        self.qt.app.screenAdded.emit(self.qt.Screen((4000, 0, 100, 100)))
        self.assertEqual(len(self.qt.windows), 2)


class InitializationTests(NativeHarness):
    def setUp(self):
        super().setUp()
        self.qt = QtFakes()
        self.gui = load('overlay_init_test', 'HostDesktopGUI/brightness_overlay.py', dict(self.dependencies, **self.qt.modules))

    def main_window_overlay_setup(self):
        tree = ast.parse((BACKEND / 'HostDesktopGUI/main_window.py').read_text())
        main = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
        init = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
        statement = next(n for n in init.body if isinstance(n, ast.Try) and any(
            isinstance(child, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == '_brightness_overlay' for t in child.targets)
            for child in n.body))
        owner = stub()
        exec(compile(ast.Module(body=[statement], type_ignores=[]), 'window_overlay_setup', 'exec'),
             {'self': owner, 'create_brightness_overlay': self.gui.create_brightness_overlay, '_brightness_log': self.log})
        return owner

    def assert_rolled_back_and_native_available(self):
        owner = self.main_window_overlay_setup()
        self.assertIsNone(owner._brightness_overlay)
        self.assertEqual(self.registry.overlay_state(), (None, True, False))
        self.assertTrue(any('Overlay initialization failed' in call.args[0] for call in self.log.call_args_list))
        manager = self.qt.qobjects[-1]
        self.assertTrue(manager._closed)
        self.assertTrue(manager.deleted)
        self.assertTrue(manager._executor._shutdown)
        self.assertIsNone(manager.bridge._post)
        self.assertEqual(self.qt.app.screenAdded.slots, [])
        self.assertEqual(self.qt.app.screenRemoved.slots, [])
        self.assertEqual(self.qt.app.aboutToQuit.slots, [])
        self.assertTrue(all(not s.geometryChanged.slots for s in self.qt.screens))
        self.assertEqual(self.qt.windows, [])
        manager.destroyed.emit()  # Deferred destruction of failed init must not close native brightness.
        self.assertFalse(self.registry.overlay_state()[2])
        self.assertEqual(self.controller().get_current_brightness(), 42)
        self.config.Brightness.MODE = 2
        self.assertEqual(self.controller().get_current_brightness(), 75)

    def test_missing_enum_does_not_break_hardware_or_gamma_startup(self):
        delattr(self.qt.qt, 'QueuedConnection')
        self.assert_rolled_back_and_native_available()

    def test_connect_failure_disconnects_partial_setup(self):
        connect = self.qt.app.screenRemoved.connect
        def partial_connect(*args):
            connect(*args)
            raise RuntimeError('connect failed after attachment')
        self.qt.app.screenRemoved.connect = partial_connect
        register = Mock(wraps=self.gui.register_overlay_bridge)
        self.gui.register_overlay_bridge = register
        self.assert_rolled_back_and_native_available()
        register.assert_not_called()

    def test_registration_failure_rolls_back_all_connections(self):
        self.gui.register_overlay_bridge = Mock(side_effect=RuntimeError('register failed'))
        self.assert_rolled_back_and_native_available()

    def test_registration_that_publishes_then_raises_is_unregistered(self):
        def register(bridge):
            self.registry.register_overlay_bridge(bridge)
            raise RuntimeError('partial register failed')
        self.gui.register_overlay_bridge = register
        self.assert_rolled_back_and_native_available()

    def test_successful_registration_is_last_after_qt_connections(self):
        register = self.gui.register_overlay_bridge
        def last_step(bridge):
            manager = self.qt.qobjects[-1]
            self.assertEqual(len(manager.requested.slots), 1)
            self.assertEqual(len(manager.destroyed.slots), 1)
            self.assertEqual(len(self.qt.app.aboutToQuit.slots), 1)
            self.assertTrue(all(len(s.geometryChanged.slots) == 1 for s in self.qt.screens))
            return register(bridge)
        self.gui.register_overlay_bridge = last_step
        manager = self.gui.BrightnessOverlayManager(object())
        try:
            self.assertIs(self.registry.overlay_state()[0], manager.bridge)
        finally:
            manager.shutdown()
            manager._executor.shutdown(wait=True)


if __name__ == '__main__':
    unittest.main()
