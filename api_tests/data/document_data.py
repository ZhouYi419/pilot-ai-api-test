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
    file_content = f"TestPilot AI 自动化测试文档\nsuffix={suffix}\n"

    return file_name, file_content.encode("utf-8"), "text/plain"