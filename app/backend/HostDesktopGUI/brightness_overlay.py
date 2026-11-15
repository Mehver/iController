# SPDX-License-Identifier: BSD-3-Clause
"""GUI-only dimming windows and a bounded, cancellable backend bridge."""

from concurrent.futures import ThreadPoolExecutor
import threading
import weakref

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QApplication, QWidget

from HostCore.brightness_controller import register_overlay_bridge, unregister_overlay_bridge
from HostCore.utils.check_platform import get_platform


class _Request:
    def __init__(self, kind, value):
        self.kind, self.value = kind, value
        self.event = threading.Event()
        self.cancelled = self.done = False
        self.committed_effects = self.inflight_effects = 0
        self.brightness_committed = False
        self.result = self.error = None


class OverlayBridge:
    """No Qt-thread wait, nor request lock held during native calls.

    A granted callback is committed before the lock is released. Cancellation
    rejects new commits; it cannot revoke a granted callback that has not yet
    been physically scheduled, or interrupt one already executing.
    """

    def __init__(self, post, is_main_thread, direct, timeout=1.5):
        self._post, self._is_main_thread, self._direct = post, is_main_thread, direct
        self._timeout = timeout
        self._lock = threading.RLock()
        self._pending = set()
        self._closed = False
        self._value = 100

    def call(self, kind, value=None):
        with self._lock:
            if self._closed:
                raise RuntimeError('Overlay bridge is closed.')
            if kind == 'get':
                return self._value  # Last successful target; no Qt operation or event-loop wait.
            direct = self._direct if self._is_main_thread() else None
            if direct is None:
                request = _Request(kind, value)
                self._pending.add(request)
                try:
                    self._post(request)  # Explicit queued signal; never BlockingQueuedConnection.
                except Exception:
                    self.close()
                    raise
        if direct is not None:
            result = direct(kind, value)
            self.remember(result)
            return result
        request.event.wait(self._timeout)
        with self._lock:
            if not request.done:
                request.cancelled = True
                self._pending.discard(request)
                if request.committed_effects:
                    raise RuntimeError('Overlay GUI request timed out; committed operations may complete before rollback.')
                raise RuntimeError('Overlay GUI request timed out before any operation was committed.')
            if request.error is not None:
                raise request.error
            return request.result

    def begin(self, request):
        with self._lock:
            return not self._closed and not request.cancelled

    def _commit_effect(self, request, *, brightness=False):
        # Linearization point: grant ONE callback before releasing the lock.
        # It is committed even if scheduling delays its physical native call.
        with self._lock:
            if self._closed or (request is not None and request.cancelled):
                raise RuntimeError('Overlay request cancelled; operation was not committed.')
            if request is not None:
                request.committed_effects += 1
                request.inflight_effects += 1
                request.brightness_committed |= brightness

    def run_effect(self, request, callback, *, brightness=False):
        """Cancel uncommitted actions, not granted callbacks; never lock native IO."""
        self._commit_effect(request, brightness=brightness)
        try:
            return callback()
        finally:
            if request is not None:
                with self._lock:
                    request.inflight_effects -= 1

    def finish(self, request, result=None, error=None):
        with self._lock:
            self._pending.discard(request)
            if self._closed or request.cancelled:
                return False
            request.result, request.error, request.done = result, error, True
            if error is None and request.kind in ('set', 'clear'):
                self._value = result
            request.event.set()
            return True

    def remember(self, target):
        with self._lock:
            self._value = target

    def close(self):
        with self._lock:
            self._closed = True
            self._post = self._direct = self._is_main_thread = None
            for request in self._pending:
                request.cancelled = request.done = True
                request.error = RuntimeError('Overlay bridge is closed; committed operations may finish during cleanup.')
                request.event.set()
            self._pending.clear()


class _OverlayWindow(QWidget):
    def __init__(self, screen, effect=lambda callback: callback()):
        flags = (Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                 | Qt.WindowDoesNotAcceptFocus | Qt.WindowTransparentForInput)
        super().__init__(None, flags)  # Independent of the host window's minimize/hide state.
        for attribute, enabled in ((Qt.WA_TranslucentBackground, True),
                                   (Qt.WA_TransparentForMouseEvents, True),
                                   (Qt.WA_ShowWithoutActivating, True),
                                   (Qt.WA_AcceptTouchEvents, False)):
            effect(lambda a=attribute, e=enabled: self.setAttribute(a, e))
        effect(lambda: self.setFocusPolicy(Qt.NoFocus))
        effect(self.winId)  # Bind the native window to its QScreen before positioning it.
        effect(lambda: self.windowHandle().setScreen(screen))
        effect(lambda: self.setGeometry(screen.geometry()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))


def _log(message):
    try:
        from HostCore.infra.files.log_manager import LogManager
        LogManager.log_console(message)
    except Exception:
        pass


def _apply_mode():
    try:
        from HostCore.brightness_controller import get_brightness_controller
        controller = get_brightness_controller()
        if controller is not None:
            controller.apply_mode()
    except Exception as error:
        _log(f'Brightness mode could not be applied: {error}')


def _shutdown_mode():
    try:
        from HostCore.brightness_controller import get_brightness_controller
        controller = get_brightness_controller()
        if controller is not None:
            controller.shutdown()
    except Exception as error:
        _log(f'Brightness cleanup failed: {error}')


def _dispose_windows(windows):
    cleared = True
    for screen, window in list(windows.items()):
        try:
            window.hide()
            window.close()
            window.deleteLater()
        except RuntimeError as error:
            if 'already deleted' not in str(error):
                cleared = False
                _log(f'Overlay window cleanup failed: {error}')
                continue
        except Exception as error:
            cleared = False
            _log(f'Overlay window cleanup failed: {error}')
            continue
        windows.pop(screen, None)
    return cleared


class BrightnessOverlayManager(QObject):
    requested = Signal(object)

    def __init__(self, owner):
        super().__init__(owner)
        self._app = QApplication.instance()
        self._target, self._closed = 100, False
        self._windows, self._screen_slots = {}, {}
        self._executor = None
        self._jobs = []
        self._connections = []
        self._registration = [False]
        self.bridge = None
        try:
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='brightness-mode')
            self.bridge = OverlayBridge(self.requested.emit,
                                        lambda: QThread.currentThread() == self._app.thread(), self._direct_call)
            self._connect(self.requested, self._dispatch, Qt.QueuedConnection)
            for screen in self._app.screens():
                self._screen_added(screen)
            self._connect(self._app.screenAdded, self._screen_added)
            self._connect(self._app.screenRemoved, self._screen_removed)
            self._connect(self._app.aboutToQuit, self.shutdown)
            self._connect(self.destroyed, self._destruction_callback())
            # Publish only after all Qt setup succeeds. A failed registration
            # may itself have partially published, so rollback still unregisters.
            register_overlay_bridge(self.bridge)
            self._registration[0] = True
        except Exception:
            self._abort_initialization()
            raise

    def _connect(self, signal, callback, *args):
        self._connections.append((signal, callback))
        signal.connect(callback, *args)

    def _abort_initialization(self):
        self._closed = True
        if self.bridge is not None:
            self.bridge.close()
            unregister_overlay_bridge(self.bridge, cleared=_dispose_windows(self._windows))
        for screen, callback in list(self._screen_slots.items()):
            try:
                screen.geometryChanged.disconnect(callback)
            except Exception:
                pass
        self._screen_slots.clear()
        for signal, callback in reversed(self._connections):
            try:
                signal.disconnect(callback)
            except Exception:
                pass
        self._connections.clear()
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)
        try:
            self.deleteLater()
        except RuntimeError:
            pass

    def _destruction_callback(self):
        # No QObject is captured by this destruction fallback. Late backend
        # calls are cancelled even if the manager is deleted outside normal quit.
        bridge, windows, screen_slots = self.bridge, self._windows, self._screen_slots
        executor, registration = self._executor, self._registration
        manager_ref = weakref.ref(self)
        def destroyed(*args):
            manager = manager_ref()
            if manager is not None:
                manager._closed = True
            bridge.close()
            unregister_overlay_bridge(bridge, cleared=_dispose_windows(windows), closing=registration[0])
            for screen, callback in list(screen_slots.items()):
                try:
                    screen.geometryChanged.disconnect(callback)
                except (RuntimeError, TypeError):
                    pass
            screen_slots.clear()
            try:
                if registration[0]:
                    executor.submit(_shutdown_mode)
                executor.shutdown(wait=False)
            except RuntimeError:
                pass  # Normal shutdown already closed the executor.
        return destroyed

    def _assert_main(self):
        if QThread.currentThread() != self._app.thread():
            raise RuntimeError('Overlay windows must be operated on the Qt main thread.')

    def _screen_added(self, screen):
        if self._closed or screen in self._screen_slots:
            return
        callback = lambda geometry, s=screen: self._align_screen(s)
        self._screen_slots[screen] = callback
        screen.geometryChanged.connect(callback)
        if self._target < 100:
            try:
                self._show_screen(screen, self._target)
            except Exception as error:
                _log(f'Overlay screen setup failed: {error}')
                try:
                    self.bridge.remember(self._perform('clear', None))
                except Exception as failure:
                    _log(f'Overlay clearance failed: {failure}')
                    self.bridge.close()

    def _align_screen(self, screen):
        if self._closed:
            return
        self._assert_main()
        if screen in self._windows:
            self._windows[screen].windowHandle().setScreen(screen)
            self._windows[screen].setGeometry(screen.geometry())

    def _screen_removed(self, screen):
        callback = self._screen_slots.pop(screen, None)
        if callback is not None:
            try:
                screen.geometryChanged.disconnect(callback)
            except (RuntimeError, TypeError):
                pass
        window = self._windows.pop(screen, None)
        if window is not None:
            remaining = {screen: window}
            if not _dispose_windows(remaining):
                self._windows.update(remaining)
                self.bridge.close()  # Do not claim a removed screen's effect was cleared.

    def _effect(self, request, callback, *, brightness=False):
        if self._closed:
            raise RuntimeError('Overlay manager is closed.')
        return self.bridge.run_effect(request, callback, brightness=brightness)

    def _show_screen(self, screen, target, request=None):
        if screen not in self._windows:
            effect = lambda callback: self._effect(request, callback)
            self._windows[screen] = effect(lambda: _OverlayWindow(screen, effect))
        window = self._windows[screen]
        self._effect(request, lambda: window.windowHandle().setScreen(screen))
        self._effect(request, lambda: window.setGeometry(screen.geometry()))  # Full screen geometry.
        self._effect(request, lambda: window.setWindowOpacity((100 - target) / 100 * 0.9), brightness=True)
        self._effect(request, window.show, brightness=True)

    def _perform(self, kind, value, request=None):
        if self._closed:
            raise RuntimeError('Overlay manager is closed.')
        self._assert_main()
        if kind == 'get':
            return self._target
        target = 100 if kind == 'clear' else value
        if kind not in ('clear', 'set') or type(target) is not int or not 0 <= target <= 100:
            raise ValueError('Overlay target must be 0..100.')
        if target == 100:
            for window in self._windows.values():
                self._effect(request, window.hide, brightness=True)
        else:
            screens = self._app.screens()
            if not screens:
                raise RuntimeError('No GUI screens are available.')
            for screen in screens:
                self._show_screen(screen, target, request)
        self._effect(request, lambda: setattr(self, '_target', target))
        return target

    @Slot(object)
    def _dispatch(self, request):
        if not self.bridge.begin(request):
            return
        previous, error = self._target, None
        try:
            result = self._perform(request.kind, request.value, request)
        except Exception as failure:
            result, error = None, failure
        accepted = self.bridge.finish(request, result, error)
        if request.brightness_committed and (error is not None or not accepted):
            # A committed operation may run after cancellation, even if native
            # execution had not begun. Stop new commits and roll back afterward.
            self._rollback(previous)

    def _rollback(self, previous):
        try:
            if not self._closed:
                self._perform('set', previous)
        except Exception as failure:
            _log(f'Overlay rollback failed: {failure}')
            self.bridge.close()

    def _direct_call(self, kind, value):
        previous = self._target
        try:
            return self._perform(kind, value)
        except Exception:
            self._rollback(previous)
            raise

    def apply_mode(self, mode):
        if not self._closed:
            # The signal is a notification; the worker consumes the committed
            # generation (including A -> B -> A), never this stale argument.
            self._jobs = [job for job in self._jobs if not job.done()]
            self._jobs.append(self._executor.submit(_apply_mode))

    @Slot()
    def shutdown(self):
        if self._closed:
            return
        self._assert_main()
        self._closed = True
        self.bridge.close()  # Release worker waiters before native cleanup takes its lock.
        cleared = _dispose_windows(self._windows)
        unregister_overlay_bridge(self.bridge, cleared=cleared, closing=True)
        for screen in list(self._screen_slots):
            self._screen_removed(screen)
        for signal, callback in ((self._app.screenAdded, self._screen_added),
                                 (self._app.screenRemoved, self._screen_removed)):
            try:
                signal.disconnect(callback)
            except (RuntimeError, TypeError):
                pass
        for job in self._jobs:
            job.cancel()
        # No QObject/callback is passed to the worker; GUI never waits on a
        # native lock. Python's executor joins before process exit; Gamma also
        # retains its original atexit recovery as a final best effort.
        self._executor.submit(_shutdown_mode)
        self._executor.shutdown(wait=False)


def create_brightness_overlay(owner):
    return BrightnessOverlayManager(owner) if get_platform() == 'Windows' else None
