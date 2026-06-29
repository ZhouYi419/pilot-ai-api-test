import time

def unique_suffix():
    return str(int(time.time() * 1000))

def build_project_create_payload():
    suffix = unique_suffix()

    return {
        "projectName": f"自动化测试项目-{suffix}",
        "projectCode": f"auto_project_{suffix}",
        "description": "接口自动化测试创建的项目",
        "ownerName": "pytest",
        "status": 1,
    }

def build_project_update_payload():
    suffix = unique_suffix()

    return {
        "projectName": f"自动化测试项目-更新-{suffix}",
        "description": "接口自动化测试更新的项目",
        "ownerName": "pytest-updated",
        "status": 1,
    }

def build_invalid_project_payload():
    return {
        "projectName": "",
        "projectCode": "",
        "description": "invalid",
        "ownerName": "pytest",
        "status": 1,
    }