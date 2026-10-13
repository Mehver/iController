# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

"""Process-local Windows software dimming backed by GDI gamma ramps."""

import atexit
import ctypes
from ctypes import wintypes
import threading


DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001
_SAFE_MINIMUM_GAIN = 0.5
_GammaRamp = (wintypes.WORD * 256) * 3


class WindowsGammaError(RuntimeError):
    pass


class _DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    )


def _scaled_ramp(baseline, percent):
    percent = max(0, min(100, int(percent)))
    # Some Windows display drivers reject aggressive ramps. Keep 0% at a
    # conservative 50% gamma gain rather than claiming physical black/off.
    gain = _SAFE_MINIMUM_GAIN + (1.0 - _SAFE_MINIMUM_GAIN) * percent / 100.0
    return tuple(
        tuple(min(65535, max(0, round(value * gain))) for value in channel)
        for channel in baseline
    )


class _Win32GammaAPI:
    """Small ctypes boundary, injectable so tests never need a real Win32 API."""

    def __init__(self, user32=None, gdi32=None):
        if user32 is None or gdi32 is None:
            win_dll = getattr(ctypes, "WinDLL", None)
            if win_dll is None:
                raise WindowsGammaError("Windows GDI is unavailable.")
            user32 = user32 or win_dll("user32", use_last_error=True)
            gdi32 = gdi32 or win_dll("gdi32", use_last_error=True)
        self._user32 = user32
        self._gdi32 = gdi32
        self._configure_signatures()

    def _configure_signatures(self):
        self._user32.EnumDisplayDevicesW.argtypes = (
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.POINTER(_DISPLAY_DEVICEW),
            wintypes.DWORD,
        )
        self._user32.EnumDisplayDevicesW.restype = wintypes.BOOL
        self._gdi32.CreateDCW.argtypes = (
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            ctypes.c_void_p,
        )
        self._gdi32.CreateDCW.restype = ctypes.c_void_p
        for function_name in ("GetDeviceGammaRamp", "SetDeviceGammaRamp"):
            function = getattr(self._gdi32, function_name)
            function.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
            function.restype = wintypes.BOOL
        self._gdi32.DeleteDC.argtypes = (ctypes.c_void_p,)
        self._gdi32.DeleteDC.restype = wintypes.BOOL

    def enumerate_display_sources(self):
        sources = []
        index = 0
        while True:
            display = _DISPLAY_DEVICEW()
            display.cb = ctypes.sizeof(display)
            if not self._user32.EnumDisplayDevicesW(None, index, ctypes.byref(display), 0):
                break
            if (
                display.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
                and display.DeviceName
            ):
                sources.append(display.DeviceName)
            index += 1
        return sources

    def _create_dc(self, source):
        dc = self._gdi32.CreateDCW("DISPLAY", source, None, None)
        if not dc:
            raise WindowsGammaError(f"Could not open display source {source}.")
        return dc

    def get_gamma_ramp(self, source):
        dc = self._create_dc(source)
        try:
            ramp = _GammaRamp()
            if not self._gdi32.GetDeviceGammaRamp(dc, ctypes.byref(ramp)):
                raise WindowsGammaError(f"Could not read gamma ramp for {source}.")
            return tuple(tuple(channel) for channel in ramp)
        finally:
            self._gdi32.DeleteDC(dc)

    def set_gamma_ramp(self, source, values):
        dc = self._create_dc(source)
        try:
            ramp = _GammaRamp()
            for channel_index, channel in enumerate(values):
                for value_index, value in enumerate(channel):
                    ramp[channel_index][value_index] = value
            if not self._gdi32.SetDeviceGammaRamp(dc, ctypes.byref(ramp)):
                raise WindowsGammaError(f"Could not set gamma ramp for {source}.")
        finally:
            self._gdi32.DeleteDC(dc)


class WindowsGammaBrightness:
    """Software brightness whose baseline and value survive controller instances."""

    _lock = threading.RLock()
    _api = None
    _baselines = {}
    _modified_sources = set()
    _current_percent = 100
    _atexit_registered = False

    @classmethod
    def _get_api(cls):
        if cls._api is None:
            cls._api = _Win32GammaAPI()
        return cls._api

    @classmethod
    def _initialize_sources(cls):
        try:
            sources = cls._get_api().enumerate_display_sources()
        except Exception as error:
            raise WindowsGammaError("No usable Windows display source.") from error

        usable_sources = []
        for source in sources:
            if source not in cls._baselines:
                try:
                    cls._baselines[source] = cls._get_api().get_gamma_ramp(source)
                except Exception:
                    continue
            usable_sources.append(source)
        if not usable_sources:
            raise WindowsGammaError("No usable Windows display source.")
        if not cls._atexit_registered:
            atexit.register(cls._restore_at_exit)
            cls._atexit_registered = True
        return usable_sources

    @classmethod
    def get_brightness(cls):
        with cls._lock:
            cls._initialize_sources()
            return cls._current_percent

    @classmethod
    def set_brightness(cls, percent):
        percent = max(0, min(100, int(percent)))
        with cls._lock:
            sources = cls._initialize_sources()
            successes = 0
            for source in sources:
                try:
                    ramp = _scaled_ramp(cls._baselines[source], percent)
                    cls._get_api().set_gamma_ramp(source, ramp)
                    cls._modified_sources.add(source)
                    successes += 1
                except Exception:
                    continue
            if not successes:
                raise WindowsGammaError("Software brightness could not be applied.")
            cls._current_percent = percent

    @classmethod
    def restore(cls):
        with cls._lock:
            restored = False
            for source in tuple(cls._modified_sources):
                try:
                    cls._get_api().set_gamma_ramp(source, cls._baselines[source])
                    cls._modified_sources.discard(source)
                    restored = True
                except Exception:
                    continue
            if restored and not cls._modified_sources:
                cls._current_percent = 100

    @classmethod
    def _restore_at_exit(cls):
        try:
            cls.restore()
        except Exception:
            pass
