import yaml
import os


class Config:
    # 默认配置 default values
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
        SERVER_CONNECTION_LOG = False

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
        # 检查配置文件是否存在
        # check if the configuration file exists
        if os.path.exists(config_path):
            # 读取配置文件，如果有新增的配置项，就触发更新
            # read the configuration file, if there are new configuration items, trigger an update
            results = [
                Config.try_get_value(config_path, Config.Control, 'TPad_SENSITIVITY'),
                Config.try_get_value(config_path, Config.Control, 'MWheel_SENSITIVITY'),
                Config.try_get_value(config_path, Config.Control, 'MWheel_CONSTANT'),
                Config.try_get_value(config_path, Config.HttpServer, 'HOST'),
                Config.try_get_value(config_path, Config.HttpServer, 'PORT'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_CHECK_MODE'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_BLACKLIST'),
                Config.try_get_value(config_path, Config.HttpServer, 'IP_WHITELIST'),
                Config.try_get_value(config_path, Config.Log, 'SERVER_ACTION_LOG'),
                Config.try_get_value(config_path, Config.Log, 'SERVER_CONNECTION_LOG')
            ]
            # 检查results列表中是否有任何一个False，如果有，就执行更新
            if not all(results):
                Config.save()

        else:
            # 文件不存在，则用默认值初始化，并保存这些默认值
            # if the file does not exist, initialize with default values and save these default values
            Config.save()

    @staticmethod
    def save():
        config_path = "./config.yaml"
        data = {
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
                'SERVER_CONNECTION_LOG': Config.Log.SERVER_CONNECTION_LOG
            }
        }
        with open(config_path, 'w') as file:
            yaml.safe_dump(data, file, sort_keys=False)
