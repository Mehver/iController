import platform

def get_platform():
    return platform.system()

def is_mac():
    return get_platform() == "Darwin"
