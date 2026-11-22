# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import threading

import screen_brightness_control as sbc
from monitorcontrol import get_monitors

from HostCore.brightness_controller.base import BaseBrightnessController, BrightnessUnsupportedError
from HostCore.brightness_controller import overlay_state
from HostCore.brightness_controller.windows_gamma import WindowsGammaBrightness
from HostCore.infra.files.config import Config
from HostCore.infra.files.log_manager import LogManager


def _log(message):
    try:
        LogManager.log_console(message)
    except Exception:
        pass


class WindowsBrightnessController(BaseBrightnessController):
    _mode_lock = threading.Lock()
    _active_mode = 0
    _applied_generation = 0
    _overlay_active = False  # Actual or possibly committed overlay writes, including MODE 0 fallback.
    _fallback_logged = False

    @classmethod
    def _cleanup_locked(cls):
        if cls._active_mode == 2:
            if WindowsGammaBrightness.restore():
                raise RuntimeError('Gamma restore failed; refusing to mix brightness modes.')
        if cls._active_mode == 1 or cls._overlay_active:
            bridge, cleared, _ = overlay_state()
            if bridge is not None:
                bridge.call('clear')
            elif not cleared:
                raise RuntimeError('Overlay clearance could not be confirmed.')
            cls._overlay_active = False

    @classmethod
    def _switch_locked(cls):
        generation, mode = Config.Brightness.committed()
        Config.Brightness.validate_mode(mode)
        if generation != cls._applied_generation or mode != cls._active_mode:
            cls._cleanup_locked()
            # Overlay clearance may have waited for Qt. Consume the latest
            # committed intent, not the target observed before that wait.
            generation, mode = Config.Brightness.committed()
            Config.Brightness.validate_mode(mode)
            if overlay_state()[2]:
                raise RuntimeError('Brightness control is shutting down.')
            if mode == 1 and overlay_state()[0] is None:
                raise RuntimeError('Overlay brightness requires the desktop GUI; unavailable in CLI.')
            cls._active_mode = mode
            cls._applied_generation = generation
            cls._fallback_logged = False
        return mode

    @classmethod
    def apply_mode(cls):
        with cls._mode_lock:
            if overlay_state()[2]:
                return
            try:
                cls._switch_locked()
                return cls._applied_generation
            except Exception as error:
                _log(f'Brightness mode change failed: {error}')
                raise BrightnessUnsupportedError() from error

    @classmethod
    def shutdown(cls):
        with cls._mode_lock:
            try:
                cls._cleanup_locked()
                cls._active_mode = 0
            except Exception as error:
                _log(f'Brightness shutdown cleanup failed: {error}')

    @staticmethod
    def _hardware_get():
        try:
            for brightness in sbc.get_brightness():
                if brightness is not None:
                    return int(brightness)
        except Exception:
            pass
        try:
            for monitor in get_monitors():
                try:
                    with monitor:
                        return int(monitor.get_luminance())
                except Exception:
                    continue
        except Exception:
            pass
        raise BrightnessUnsupportedError()

    @staticmethod
    def _hardware_set(value):
        try:
            result = sbc.set_brightness(value, no_return=False)
            # Pinned SBC 0.27.2: no_return=False yields a readback list, with
            # None entries for failed displays. None is normal ONLY when
            # no_return=True; empty/all-None results are not confirmed success.
            if isinstance(result, (list, tuple)) and any(v is not None for v in result):
                return
        except Exception:
            pass
        success = False
        try:
            for monitor in get_monitors():
                try:
                    with monitor:
                        monitor.set_luminance(value)
                    success = True
                except Exception:
                    continue
        except Exception:
            pass
        if not success:
            raise BrightnessUnsupportedError()

    @classmethod
    def _overlay(cls, value=None, *, fallback=False):
        bridge, _, _ = overlay_state()
        if fallback and not cls._fallback_logged:
            _log('Hardware brightness unavailable; using GUI overlay fallback.' if bridge is not None else
                 'Hardware brightness unavailable; overlay fallback requires an active desktop GUI bridge; unavailable in CLI or after overlay initialization failure.')
            cls._fallback_logged = True
        if bridge is None:
            if fallback:
                raise BrightnessUnsupportedError()
            raise RuntimeError('Overlay brightness requires the desktop GUI; unavailable in CLI.')
        # A pure read cannot select the writer: hardware get may fail while
        # hardware set still works. Only writes may commit an overlay effect.
        if value is not None:
            # Set before waiting, including value 0: failed/timed-out writes
            # may already be committed. Keep active until confirmed cleanup.
            cls._overlay_active = True
        return bridge.call('get' if value is None else 'set', value)

    def _operate(self, value=None):
        with self._mode_lock:
            try:
                if overlay_state()[2]:
                    raise RuntimeError('Brightness control is shutting down.')
                mode = self._switch_locked()
                if mode == 0:
                    if not self._overlay_active:
                        try:
                            return self._hardware_get() if value is None else self._hardware_set(value)
                        except BrightnessUnsupportedError:
                            pass
                    return self._overlay(value, fallback=True)
                if mode == 2:
                    return (WindowsGammaBrightness.get_brightness() if value is None
                            else WindowsGammaBrightness.set_brightness(value))
                return self._overlay(value)
            except BrightnessUnsupportedError:
                raise
            except Exception as error:
                _log(f'Brightness mode operation failed: {error}')
                raise BrightnessUnsupportedError() from error

    def get_current_brightness(self):
        return self._operate()

    def set_brightness(self, target_brightness):
        # Preserve the Gamma adapter's public clamp convention for all modes.
        self._operate(max(0, min(100, int(target_brightness))))
