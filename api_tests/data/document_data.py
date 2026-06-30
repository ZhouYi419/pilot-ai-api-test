import time

def unique_suffix():
    return str(int(time.time() * 1000))

def build_document_upload_form():
    suffix = unique_suffix()

    return {
        "documentName": f"自动化测试文档-{suffix}",
        "version": f"v{suffix}",
        "documentType": "MODULE_SPEC",
        "description": "接口自动化测试上传的文档",
        "currentVersion": "true",
    }

def build_invalid_document_upload_form():
    return {
        "documentName": "",
        "version": "",
        "documentType": "",
        "description": "invalid",
        "currentVersion": "true",
    }

def build_txt_file():
    suffix = unique_suffix()
    file_name = f"auto-document-{suffix}.txt"
    file_content = f"""
    # 登录模块说明
    
    ## 功能概述
    
    登录模块用于验证用户身份，支持账号密码登录。用户输入账号和密码后，系统校验账号状态、密码正确性以及登录权限。
    
    ## 前置条件
    
    1. 用户账号已经创建。
    2. 用户账号处于启用状态。
    3. 用户已经打开登录页面。
    
    ## 正常流程
    
    1. 用户输入账号。
    2. 用户输入密码。
    3. 用户点击登录按钮。
    4. 系统校验账号和密码。
    5. 系统生成访问令牌。
    6. 系统跳转到首页。
    
    ## 异常流程
    
    1. 如果账号不存在，系统提示账号或密码错误。
    2. 如果密码错误，系统提示账号或密码错误。
    3. 如果账号被停用，系统提示账号不可用。
    
    ## 接口说明
    
    POST /api/auth/login
    
    请求参数：
    - username：登录账号
    - password：登录密码
    
    响应字段：
    - token：访问令牌
    - expiresAt：过期时间
    
    ## 业务规则
    
    1. 密码连续错误超过 5 次后锁定账号。
    2. 登录成功后需要记录登录日志。
    3. 访问令牌默认有效期为 2 小时。
    
    suffix={suffix}
    """

    return file_name, file_content.encode("utf-8"), "text/plain"