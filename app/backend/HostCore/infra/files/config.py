# BSD 3-Clause License
#
# Copyright (c) 2024 Mehver (https://github.com/Mehver). All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import yaml
import os

_MODE_UNSET = object()


class _BrightnessMode(type):
    @property
    def MODE(cls):
        return cls._committed[1]

    @MODE.setter
    def MODE(cls, mode):
        mode = cls.validate_mode(mode)
        generation, previous = cls._committed
        if mode != previous:
            cls._committed = (generation + 1, mode)


class Config:
    # 默认配置 default values
    class Brightness(metaclass=_BrightnessMode):
        _committed = (0, 0)  # One publication: change generation, MODE integer.

        @classmethod
        def committed(cls):
            return cls._committed

        @staticmethod
        def validate_mode(mode):
            if type(mode) is not int or mode not in (0, 1, 2):
                raise ValueError('Brightness.MODE must be an integer: 0, 1 or 2.')
            return mode

    class Control:
        TPad_SENSITIVITY = 1
        MWheel_SENSITIVITY = 1
        MWheel_CONSTANT = 0

    class HttpServer:
        HOST = "0.0.0.0"
        PORT = 3030
        IP_CHECK_MODE = "blacklist"
        IP_BLACKLIST = []
        IP_WHITELIST = ["127.0.0.1"]

    class Log:
        SERVER_ACTION_LOG = True
        SERVER_IPS_LOG = True
        SERVER_CONNECTION_LOG = False
        KEYBOARD_TEXT_LOG = False

    class Gui:
        # GUI 面板专用配置（CLI 模式忽略）
        LANGUAGE_FOLLOW_SYSTEM = True
        LANGUAGE = "zh"  # zh / en（不跟随系统时生效）
        THEME_FOLLOW_SYSTEM = True
        THEME = "light"  # light / dark（不跟随系统时生效）

    @staticmethod
    def try_get_value(config_path, config_class, config_value):
        try:
            with open(config_path, 'r') as file:
                data = yaml.safe_load(file)
                # print(f"data: {data}")
                setattr(config_class, config_value, data[config_class.__name__][config_value])
                return True
        except KeyError:
            return False

    @staticmethod
    def init():
        config_path = "./config.yaml"
        candidate_mode = 0
        # 检查配置文件是否存在
        # check if the configuration file exists
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                loaded = yaml.safe_load(file)
            if not isinstance(loaded, dict):
                raise ValueError('Configuration must be a mapping.')
            brightness = loaded.get('Brightness', {})
            if not isinstance(brightness, dict):
                raise ValueError('Brightness must be a mapping.')
            candidate_mode = Config.Brightness.validate_mode(brightness.get('MODE', 0))
            # 读取配置文件，如果有新增的配置项，就触发更新
            # read the configuration file, if there are new configuration items, trigger an update
            results = [
                'MODE' in brightness,
                Config.try_get_value(config_path, Config.Control, 'TPad_SENSITIVITY'),
                Config.try_get_value(config_path, Config.Control, 'MWheel_SENSITIVITY'),
                Config.try_get_value(config_path, Config.Control, 'MWheel_CONSTANT'),
                Config.try_get_value(config_path, Config.HttpServer, 'HOST'),
                Config.try_get_value(config_path, Config.HttpServer, 'PORT'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_CHECK_MODE'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_BLACKLIST'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_WHITELIST'),
                Config.try_get_value(config_path, Config.Log, 'SERVER_ACTION_LOG'),
                Config.try_get_value(config_path, Config.Log, 'SERVER_IPS_LOG'),
                Config.try_get_value(config_path, Config.Log, 'SERVER_CONNECTION_LOG'),
                Config.try_get_value(config_path, Config.Log, 'KEYBOARD_TEXT_LOG'),
                Config.try_get_value(config_path, Config.Gui, 'LANGUAGE_FOLLOW_SYSTEM'),
                Config.try_get_value(config_path, Config.Gui, 'LANGUAGE'),
                Config.try_get_value(config_path, Config.Gui, 'THEME_FOLLOW_SYSTEM'),
                Config.try_get_value(config_path, Config.Gui, 'THEME')
            ]
            # 检查results列表中是否有任何一个False，如果有，就执行更新
            if not all(results):
                Config.save(brightness_mode=candidate_mode)
            else:
                Config.Brightness.MODE = candidate_mode

        else:
            # 文件不存在，则用默认值初始化，并保存这些默认值
            # if the file does not exist, initialize with default values and save these default values
            Config.save(brightness_mode=candidate_mode)

    @staticmethod
    def save(*, brightness_mode=_MODE_UNSET):
        config_path = "./config.yaml"
        mode = Config.Brightness.validate_mode(Config.Brightness.MODE if brightness_mode is _MODE_UNSET else brightness_mode)
        data = {
            'Brightness': {'MODE': mode},
            'Control': {
                'TPad_SENSITIVITY': Config.Control.TPad_SENSITIVITY,
                'MWheel_SENSITIVITY': Config.Control.MWheel_SENSITIVITY,
                'MWheel_CONSTANT': Config.Control.MWheel_CONSTANT
            },
            'HttpServer': {
                'HOST': Config.HttpServer.HOST,
                'PORT': Config.HttpServer.PORT,
                'IP_CHECK_MODE': Config.HttpServer.IP_CHECK_MODE,
                'IP_BLACKLIST': Config.HttpServer.IP_BLACKLIST,
                'IP_WHITELIST': Config.HttpServer.IP_WHITELIST
            },
            'Log': {
                'SERVER_ACTION_LOG': Config.Log.SERVER_ACTION_LOG,
                'SERVER_IPS_LOG': Config.Log.SERVER_IPS_LOG,
                'SERVER_CONNECTION_LOG': Config.Log.SERVER_CONNECTION_LOG,
                'KEYBOARD_TEXT_LOG': Config.Log.KEYBOARD_TEXT_LOG
            },
            'Gui': {
                'LANGUAGE_FOLLOW_SYSTEM': Config.Gui.LANGUAGE_FOLLOW_SYSTEM,
                'LANGUAGE': Config.Gui.LANGUAGE,
                'THEME_FOLLOW_SYSTEM': Config.Gui.THEME_FOLLOW_SYSTEM,
                'THEME': Config.Gui.THEME
            }
        }
        with open(config_path, 'w') as file:
            yaml.safe_dump(data, file, sort_keys=False)
        Config.Brightness.MODE = mode  # Publish only after successful write/close.
