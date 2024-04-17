from quart import jsonify
import platform


async def get_system_info():
    os_name = platform.system()
    # os_name = 'Windows'  # 测试值
    os_name = 'Darwin'  # 测试值
    # os_version = platform.version()
    # os_arch = platform.architecture()
    # os_machine = platform.machine()
    # os_processor = platform.processor()
    return jsonify({
        "status": "success",
        "os": os_name,
    })
