import time

def build_module_create_payload():
    suffix = str(int(time.time() * 1000))

    return {
        "moduleName": f"自动化模块-{suffix}",
        "moduleCode": f"auto_module_{suffix}",
        "description": "接口自动化测试创建的模块",
        "status": 1,
    }


def build_invalid_module_payload():
    return {
        "moduleName": "",
        "moduleCode": "",
        "description": "invalid",
        "status": 1,
    }