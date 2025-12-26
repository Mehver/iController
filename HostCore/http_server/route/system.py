from quart import jsonify
import platform
from HostCore.utils.log_manager import LogManager


async def get_system_info():
    """app.route('/api/system/info', methods=['GET'])(get_system_info)"""
    os_name = platform.system()
    LogManager.log_console(f"Get system platform: {os_name}.")
    # os_name = 'Windows'  # 测试值
    # os_name = 'Darwin'  # 测试值
    # os_version = platform.version()
    # os_arch = platform.architecture()
    # os_machine = platform.machine()
    # os_processor = platform.processor()
    return jsonify({
        "status": "success",
        "os": os_name,
    })
