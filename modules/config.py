# import yaml
# import os


class Config:
    # 默认配置 default values
    class Control:
        TPad_SENSITIVITY = 1
        MWheel_SENSITIVITY = 1
        MWheel_CONSTANT = 0

    class HttpServer:
        HOST = "0.0.0.0"
        PORT = 3030

    # @staticmethod
    # def init():
    #     config_path = "./config.yaml"
    #     # 检查配置文件是否存在
    #     # check if the configuration file exists
    #     if os.path.exists(config_path):
    #         # 读取现有的配置文件
    #         with open(config_path, 'r') as file:
    #             data = yaml.safe_load(file)
    #             Config.Control.TPad_SENSITIVITY = data['Control']['TPad_SENSITIVITY']
    #             Config.Control.MWheel_SENSITIVITY = data['Control']['MWheel_SENSITIVITY']
    #             Config.Control.MWheel_CONSTANT = data['Control']['MWheel_CONSTANT']
    #             Config.HttpServer.HOST = data['HttpServer']['HOST']
    #             Config.HttpServer.PORT = data['HttpServer']['PORT']
    #     else:
    #         # 文件不存在，则用默认值初始化，并保存这些默认值
    #         # if the file does not exist, initialize with default values and save these default values
    #         Config.save()
    #
    # @staticmethod
    # def save():
    #     config_path = "./config.yaml"
    #     data = {
    #         'Control': {
    #             'TPad_SENSITIVITY': Config.Control.TPad_SENSITIVITY,
    #             'MWheel_SENSITIVITY': Config.Control.MWheel_SENSITIVITY,
    #             'MWheel_CONSTANT': Config.Control.MWheel_CONSTANT
    #         },
    #         'HttpServer': {
    #             'HOST': Config.HttpServer.HOST,
    #             'PORT': Config.HttpServer.PORT
    #         }
    #     }
    #     with open(config_path, 'w') as file:
    #         yaml.safe_dump(data, file)
