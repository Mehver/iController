# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import importlib.util
import os
import sys
import types
from unittest.mock import Mock

import pytest


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..")
WINDOWS_CONTROLLER_PATH = os.path.join(
    BACKEND_DIR, "HostCore", "volume_controller", "windows.py"
)


@pytest.fixture
def windows_volume_module(monkeypatch):
    monkeypatch.syspath_prepend(BACKEND_DIR)
    endpoint = Mock()
    speakers = Mock()
    speakers.EndpointVolume = endpoint

    pycaw_package = types.ModuleType("pycaw")
    pycaw_module = types.ModuleType("pycaw.pycaw")
    pycaw_module.AudioUtilities = Mock()
    pycaw_module.AudioUtilities.GetSpeakers.return_value = speakers
    comtypes = types.ModuleType("comtypes")
    comtypes.COINIT_MULTITHREADED = object()
    comtypes.CoInitializeEx = Mock()
    comtypes.CoUninitialize = Mock()
    monkeypatch.setitem(sys.modules, "pycaw", pycaw_package)
    monkeypatch.setitem(sys.modules, "pycaw.pycaw", pycaw_module)
    monkeypatch.setitem(sys.modules, "comtypes", comtypes)

    spec = importlib.util.spec_from_file_location(
        "windows_volume_controller_under_test", WINDOWS_CONTROLLER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, endpoint, pycaw_module, comtypes


def test_get_volume_uses_and_cleans_up_same_call(windows_volume_module):
    module, endpoint, pycaw_module, comtypes = windows_volume_module
    endpoint.GetMasterVolumeLevelScalar.return_value = 0.42

    assert module.WindowsVolumeController().get_current_volume() == 42

    comtypes.CoInitializeEx.assert_called_once_with(comtypes.COINIT_MULTITHREADED)
    pycaw_module.AudioUtilities.GetSpeakers.assert_called_once_with()
    endpoint.GetMasterVolumeLevelScalar.assert_called_once_with()
    endpoint.Release.assert_called_once_with()
    comtypes.CoUninitialize.assert_called_once_with()


def test_set_volume_uses_endpoint_and_cleans_up(windows_volume_module):
    module, endpoint, pycaw_module, comtypes = windows_volume_module

    module.WindowsVolumeController().set_volume(60)

    comtypes.CoInitializeEx.assert_called_once_with(comtypes.COINIT_MULTITHREADED)
    pycaw_module.AudioUtilities.GetSpeakers.assert_called_once_with()
    endpoint.SetMute.assert_called_once_with(0, None)
    endpoint.SetMasterVolumeLevelScalar.assert_called_once_with(0.6, None)
    endpoint.Release.assert_called_once_with()
    comtypes.CoUninitialize.assert_called_once_with()


def test_set_volume_propagates_errors_and_cleans_up(windows_volume_module):
    module, endpoint, _, comtypes = windows_volume_module
    endpoint.SetMute.side_effect = RuntimeError("set failed")

    with pytest.raises(RuntimeError, match="set failed"):
        module.WindowsVolumeController().set_volume(60)

    endpoint.SetMute.assert_called_once_with(0, None)
    endpoint.SetMasterVolumeLevelScalar.assert_not_called()
    endpoint.Release.assert_called_once_with()
    comtypes.CoUninitialize.assert_called_once_with()
