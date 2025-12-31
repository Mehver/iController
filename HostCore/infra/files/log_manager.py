import os
from datetime import datetime
from HostCore.infra.files.config import Config


class LogManager:
    log_dir = "./logs"
    ip_log_file = os.path.join(log_dir, "ips.log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    @staticmethod
    def check_new_ip(ip_address):
        """检查IP是否已记录过"""
        if os.path.exists(LogManager.ip_log_file):
            with open(LogManager.ip_log_file, 'r') as f:
                for line in f:
                    if ip_address in line:
                        return True
        return False

    @staticmethod
    def log_connection(ip_address):
        """记录连接信息"""
        # 确保日志目录存在，如果不存在则创建
        if not os.path.exists(LogManager.log_dir):
            os.makedirs(LogManager.log_dir)
        # 记录IP和首次连接时间
        if not LogManager.check_new_ip(ip_address) and Config.Log.SERVER_IPS_LOG:
            with open(LogManager.ip_log_file, 'a') as f:
                f.write(f"[{ip_address}] first connected on [{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:22]}]\n")
        # 记录详细的日志到日期文件中
        if Config.Log.SERVER_CONNECTION_LOG:
            today_log_file = os.path.join(LogManager.log_dir, datetime.now().strftime("Connect_%Y-%m-%d.log"))
            with open(today_log_file, 'a') as f:
                f.write(f"[{ip_address}] connected on [{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:22]}]\n")

    @staticmethod
    def log_console(message):
        """同步记录控制台输出"""
        print(message)
        if Config.Log.SERVER_ACTION_LOG:
            console_log_file = os.path.join(LogManager.log_dir, datetime.now().strftime("Action_%Y-%m-%d.log"))
            with open(console_log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:22]}] {message}\n")
