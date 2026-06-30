import time

import allure
import pytest

from common.assert_utils import (
    assert_error_response,
    assert_http_status,
    assert_success_response,
)
from data.document_data import (
    build_document_upload_form,
    build_invalid_document_upload_form,
    build_txt_file,
)
from data.module_data import build_module_create_payload
from data.project_data import build_project_create_payload


@pytest.fixture
def created_project(api_client):
    response = api_client.post(
        "/api/projects",
        json_body=build_project_create_payload(),
    )

    assert_http_status(response, 200)
    body = assert_success_response(response)
    project_id = body["data"]["id"]

    yield project_id

    api_client.delete(f"/api/projects/{project_id}")


@pytest.fixture
def created_module(api_client, created_project):
    response = api_client.post(
        f"/api/projects/{created_project}/modules",
        json_body=build_module_create_payload(),
    )

    assert_http_status(response, 200)
    body = assert_success_response(response)
    module_id = body["data"]["id"]

    yield module_id


@pytest.fixture
def uploaded_document(api_client, created_module):
    form = build_document_upload_form()
    file_name, file_content, content_type = build_txt_file()

    files = {
        "file": (file_name, file_content, content_type),
    }

    response = api_client.post_multipart(
        f"/api/modules/{created_module}/documents",
        files=files,
        data=form,
    )

    assert_http_status(response, 200)
    body = assert_success_response(response)
    document_id = body["data"]["id"]

    yield {
        "documentId": document_id,
        "moduleId": created_module,
        "form": form,
        "fileName": file_name,
    }

    api_client.delete(f"/api/documents/{document_id}")

@pytest.fixture
def parsed_document(api_client, uploaded_document):
    document_id = uploaded_document["documentId"]

    status_body = wait_document_parse_finished(api_client, document_id)
    assert status_body["data"]["parseStatus"] == "SUCCESS"

    return uploaded_document

@pytest.fixture
def chunked_document(api_client, parsed_document):
    document_id = parsed_document["documentId"]

    response = api_client.post(f"/api/documents/{document_id}/chunk")
    assert_http_status(response, 202)
    assert_success_response(response)

    status_body = wait_document_chunk_finished(api_client, document_id)
    assert status_body["data"]["chunkStatus"] == "SUCCESS"

    return parsed_document

@pytest.fixture
def parsed_document(api_client, uploaded_document):
    document_id = uploaded_document["documentId"]

    status_body = wait_document_parse_finished(api_client, document_id)
    assert status_body["data"]["parseStatus"] == "SUCCESS"

    return uploaded_document

@pytest.fixture
def chunked_document(api_client, parsed_document):
    document_id = parsed_document["documentId"]

    response = api_client.post(f"/api/documents/{document_id}/chunk")
    assert_http_status(response, 202)
    assert_success_response(response)

    status_body = wait_document_chunk_finished(api_client, document_id)
    assert status_body["data"]["chunkStatus"] == "SUCCESS"

    return parsed_document

def wait_document_parse_finished(api_client, document_id, timeout_seconds=10):
    deadline = time.time() + timeout_seconds
    last_body = None

    while time.time() < deadline:
        response = api_client.get(f"/api/documents/{document_id}/status")
        assert_http_status(response, 200)
        body = assert_success_response(response)
        last_body = body

        parse_status = body["data"]["parseStatus"]
        if parse_status in ["SUCCESS", "FAILED"]:
            return body

        time.sleep(0.5)

    pytest.fail(f"文档解析未在 {timeout_seconds} 秒内完成，最后状态：{last_body}")

def wait_document_chunk_finished(api_client, document_id, timeout_seconds=10):
    deadline = time.time() + timeout_seconds
    last_body = None

    while time.time() < deadline:
        response = api_client.get(f"/api/documents/{document_id}/chunk-status")
        assert_http_status(response, 200)
        body = assert_success_response(response)
        last_body = body

        chunk_status = body["data"]["chunkStatus"]
        if chunk_status in ["SUCCESS", "FAILED"]:
            return body

        time.sleep(0.5)

    pytest.fail(f"文档切片未在 {timeout_seconds} 秒内完成，最后状态：{last_body}")

def wait_document_chunk_finished(api_client, document_id, timeout_seconds=10):
    deadline = time.time() + timeout_seconds
    last_body = None

    while time.time() < deadline:
        response = api_client.get(f"/api/documents/{document_id}/chunk-status")
        assert_http_status(response, 200)
        body = assert_success_response(response)
        last_body = body

        chunk_status = body["data"]["chunkStatus"]
        if chunk_status in ["SUCCESS", "FAILED"]:
            return body

        time.sleep(0.5)

    pytest.fail(f"文档切片未在 {timeout_seconds} 秒内完成，最后状态：{last_body}")

@allure.epic("TestPilot AI")
@allure.feature("模块文档管理")
@pytest.mark.document
class TestDocumentApi:

    @allure.story("上传模块文档")
    @allure.title("上传 TXT 文档成功")
    @pytest.mark.smoke
    def test_upload_document_success(self, api_client, created_module):
        form = build_document_upload_form()
        file_name, file_content, content_type = build_txt_file()

        files = {
            "file": (file_name, file_content, content_type),
        }

        response = api_client.post_multipart(
            f"/api/modules/{created_module}/documents",
            files=files,
            data=form,
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert data["moduleId"] == created_module
        assert data["documentName"] == form["documentName"]
        assert data["version"] == form["version"]
        assert data["documentType"] == form["documentType"]
        assert data["originalFileName"] == file_name
        assert data["fileExtension"] == "txt"
        assert data["fileSize"] > 0
        assert data["currentVersion"] is True
        assert data["active"] is True

        api_client.delete(f"/api/documents/{data['id']}")

    @allure.story("上传模块文档")
    @allure.title("上传文档失败：空文件")
    def test_upload_document_without_file_failed(self, api_client, created_module):
        files = {
            "file": ("empty.txt", b"", "text/plain"),
        }

        response = api_client.post_multipart(
            f"/api/modules/{created_module}/documents",
            files=files,
            data=build_document_upload_form(),
        )

        assert_http_status(response, 400)
        assert_error_response(response, expected_code=40004)

    @allure.story("上传模块文档")
    @allure.title("上传文档失败：不支持的文件类型")
    def test_upload_document_unsupported_file_type_failed(self, api_client, created_module):
        form = build_document_upload_form()
        files = {
            "file": ("auto-document.exe", b"fake exe content", "application/octet-stream"),
        }

        response = api_client.post_multipart(
            f"/api/modules/{created_module}/documents",
            files=files,
            data=form,
        )

        assert_http_status(response, 400)
        assert_error_response(response)

    @allure.story("上传模块文档")
    @allure.title("上传文档失败：版本为空")
    def test_upload_document_invalid_form_failed(self, api_client, created_module):
        file_name, file_content, content_type = build_txt_file()
        files = {
            "file": (file_name, file_content, content_type),
        }

        response = api_client.post_multipart(
            f"/api/modules/{created_module}/documents",
            files=files,
            data=build_invalid_document_upload_form(),
        )

        assert_http_status(response, 400)
        assert_error_response(response, expected_code=40000)

    @allure.story("分页查询模块文档")
    @allure.title("分页查询模块文档成功")
    def test_query_document_page_success(self, api_client, uploaded_document):
        module_id = uploaded_document["moduleId"]

        response = api_client.get(
            f"/api/modules/{module_id}/documents",
            params={
                "pageNum": 1,
                "pageSize": 10,
                "documentType": "MODULE_SPEC",
                "currentVersion": "true",
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert "records" in body["data"]
        assert "total" in body["data"]
        assert "pageNum" in body["data"]
        assert "pageSize" in body["data"]

    @allure.story("文档详情管理")
    @allure.title("查询文档详情成功")
    def test_get_document_detail_success(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}")

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert body["data"]["id"] == document_id
        assert body["data"]["documentName"] == uploaded_document["form"]["documentName"]

        data = body["data"]

        assert data["id"] == document_id
        assert data["documentName"] == uploaded_document["form"]["documentName"]
        assert data["parseStatus"] in ["PENDING", "PARSING", "SUCCESS", "FAILED"]
        assert data["indexStatus"] in ["PENDING", "INDEXING", "SUCCESS", "FAILED"]

    @allure.story("文档详情管理")
    @allure.title("查询文档处理状态成功")
    def test_get_document_status_success(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/status")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["parseStatus"] in ["PENDING", "PARSING", "SUCCESS", "FAILED"]
        assert data["indexStatus"] in ["PENDING", "INDEXING", "SUCCESS", "FAILED"]

    @allure.story("文档详情管理")
    @allure.title("生成文档临时下载地址成功")
    def test_generate_document_download_url_success(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/download-url")

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert body["data"]["documentId"] == document_id
        assert body["data"]["fileName"]
        assert body["data"]["downloadUrl"]
        assert body["data"]["expiresAt"]

    @allure.story("文档详情管理")
    @allure.title("删除文档成功")
    def test_delete_document_success(self, api_client, created_module):
        form = build_document_upload_form()
        file_name, file_content, content_type = build_txt_file()
        files = {
            "file": (file_name, file_content, content_type),
        }

        upload_response = api_client.post_multipart(
            f"/api/modules/{created_module}/documents",
            files=files,
            data=form,
        )

        assert_http_status(upload_response, 200)
        upload_body = assert_success_response(upload_response)
        document_id = upload_body["data"]["id"]

        delete_response = api_client.delete(f"/api/documents/{document_id}")
        assert_http_status(delete_response, 200)
        assert_success_response(delete_response)

        detail_response = api_client.get(f"/api/documents/{document_id}")
        assert_http_status(detail_response, 404)
        assert_error_response(detail_response)

    @allure.story("文档详情管理")
    @allure.title("查询不存在的文档失败")
    def test_get_document_not_found(self, api_client):
        response = api_client.get("/api/documents/999999999")

        assert_http_status(response, 404)
        assert_error_response(response)

    @allure.story("文档详情管理")
    @allure.title("手动提交文档解析任务成功")
    def test_trigger_document_parse_success(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        wait_document_parse_finished(api_client, document_id)

        response = api_client.post(f"/api/documents/{document_id}/parse")

        assert_http_status(response, 202)
        body = assert_success_response(response)

        assert body["data"]["documentId"] == document_id
        assert body["data"]["parseStatus"] in ["PENDING", "PARSING", "SUCCESS", "FAILED"]

    @allure.story("文档详情管理")
    @allure.title("查询文档解析文本成功")
    def test_get_document_content_success(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        status_body = wait_document_parse_finished(api_client, document_id)
        assert status_body["data"]["parseStatus"] == "SUCCESS"

        response = api_client.get(f"/api/documents/{document_id}/content")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["documentName"] == uploaded_document["form"]["documentName"]
        assert data["version"] == uploaded_document["form"]["version"]
        assert data["detectedContentType"]
        assert data["parserName"]
        assert data["parsedCharCount"] > 0
        assert data["cleanCharCount"] > 0
        assert data["parsedContent"]
        assert data["cleanContent"]

    @allure.story("文档切片管理")
    @allure.title("提交文档切片任务成功")
    def test_trigger_document_chunk_success(self, api_client, parsed_document):
        document_id = parsed_document["documentId"]

        response = api_client.post(f"/api/documents/{document_id}/chunk")

        assert_http_status(response, 202)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["parseStatus"] == "SUCCESS"
        assert data["chunkStatus"] in ["PENDING", "CHUNKING", "SUCCESS", "FAILED"]
        assert data["indexStatus"] in ["PENDING", "INDEXING", "SUCCESS", "FAILED"]

    @allure.story("文档切片管理")
    @allure.title("查询文档切片状态成功")
    def test_get_document_chunk_status_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/chunk-status")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["parseStatus"] == "SUCCESS"
        assert data["chunkStatus"] == "SUCCESS"
        assert data["parentChunkCount"] > 0
        assert data["childChunkCount"] > 0
        assert data["chunkStartedAt"]
        assert data["chunkFinishedAt"]
        assert data["chunkDurationMs"] >= 0

    @allure.story("文档切片管理")
    @allure.title("分页查询文档知识块成功")
    def test_query_document_chunks_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(
            f"/api/documents/{document_id}/chunks",
            params={
                "pageNum": 1,
                "pageSize": 10,
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert "records" in data
        assert data["total"] > 0
        assert data["pageNum"] == 1
        assert data["pageSize"] == 10

        first_chunk = data["records"][0]
        assert first_chunk["id"]
        assert first_chunk["documentId"] == document_id
        assert first_chunk["chunkLevel"] in ["PARENT", "CHILD"]
        assert first_chunk["sectionType"]
        assert first_chunk["content"]
        assert first_chunk["chunkIndex"] >= 0
        assert first_chunk["charCount"] > 0
        assert first_chunk["tokenCount"] > 0

    @allure.story("文档切片管理")
    @allure.title("按知识块层级筛选成功")
    def test_query_document_chunks_by_level_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(
            f"/api/documents/{document_id}/chunks",
            params={
                "pageNum": 1,
                "pageSize": 10,
                "chunkLevel": "PARENT",
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)

        for item in body["data"]["records"]:
            assert item["chunkLevel"] == "PARENT"

    @allure.story("文档切片管理")
    @allure.title("树形查询父子知识块成功")
    def test_query_document_chunk_tree_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/chunks/tree")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert isinstance(data, list)
        assert len(data) > 0

        first_node = data[0]
        assert first_node["parent"]["documentId"] == document_id
        assert first_node["parent"]["chunkLevel"] == "PARENT"
        assert isinstance(first_node["children"], list)

        if first_node["children"]:
            assert first_node["children"][0]["chunkLevel"] == "CHILD"
            assert first_node["children"][0]["parentChunkId"] == first_node["parent"]["id"]

    @allure.story("文档切片管理")
    @allure.title("未解析成功的文档提交切片失败")
    def test_trigger_chunk_before_parse_finished_failed(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        response = api_client.post(f"/api/documents/{document_id}/chunk")

        if response.status_code == 202:
            body = assert_success_response(response)
            assert body["data"]["documentId"] == document_id
        else:
            assert_http_status(response, 400)
            assert_error_response(response, expected_code=40008)

    @allure.story("文档切片管理")
    @allure.title("提交文档切片任务成功")
    def test_trigger_document_chunk_success(self, api_client, parsed_document):
        document_id = parsed_document["documentId"]

        response = api_client.post(f"/api/documents/{document_id}/chunk")

        assert_http_status(response, 202)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["parseStatus"] == "SUCCESS"
        assert data["chunkStatus"] in ["PENDING", "CHUNKING", "SUCCESS", "FAILED"]
        assert data["indexStatus"] in ["PENDING", "INDEXING", "SUCCESS", "FAILED"]

    @allure.story("文档切片管理")
    @allure.title("查询文档切片状态成功")
    def test_get_document_chunk_status_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/chunk-status")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert data["documentId"] == document_id
        assert data["parseStatus"] == "SUCCESS"
        assert data["chunkStatus"] == "SUCCESS"
        assert data["parentChunkCount"] > 0
        assert data["childChunkCount"] > 0
        assert data["chunkStartedAt"]
        assert data["chunkFinishedAt"]
        assert data["chunkDurationMs"] >= 0

    @allure.story("文档切片管理")
    @allure.title("分页查询文档知识块成功")
    def test_query_document_chunks_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(
            f"/api/documents/{document_id}/chunks",
            params={
                "pageNum": 1,
                "pageSize": 10,
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert "records" in data
        assert data["total"] > 0
        assert data["pageNum"] == 1
        assert data["pageSize"] == 10

        first_chunk = data["records"][0]
        assert first_chunk["id"]
        assert first_chunk["documentId"] == document_id
        assert first_chunk["chunkLevel"] in ["PARENT", "CHILD"]
        assert first_chunk["sectionType"]
        assert first_chunk["content"]
        assert first_chunk["chunkIndex"] >= 0
        assert first_chunk["charCount"] > 0
        assert first_chunk["tokenCount"] > 0

    @allure.story("文档切片管理")
    @allure.title("按知识块层级筛选成功")
    def test_query_document_chunks_by_level_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(
            f"/api/documents/{document_id}/chunks",
            params={
                "pageNum": 1,
                "pageSize": 10,
                "chunkLevel": "PARENT",
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)

        for item in body["data"]["records"]:
            assert item["chunkLevel"] == "PARENT"

    @allure.story("文档切片管理")
    @allure.title("树形查询父子知识块成功")
    def test_query_document_chunk_tree_success(self, api_client, chunked_document):
        document_id = chunked_document["documentId"]

        response = api_client.get(f"/api/documents/{document_id}/chunks/tree")

        assert_http_status(response, 200)
        body = assert_success_response(response)
        data = body["data"]

        assert isinstance(data, list)
        assert len(data) > 0

        first_node = data[0]
        assert first_node["parent"]["documentId"] == document_id
        assert first_node["parent"]["chunkLevel"] == "PARENT"
        assert isinstance(first_node["children"], list)

        if first_node["children"]:
            assert first_node["children"][0]["chunkLevel"] == "CHILD"
            assert first_node["children"][0]["parentChunkId"] == first_node["parent"]["id"]

    @allure.story("文档切片管理")
    @allure.title("未解析成功的文档提交切片失败")
    def test_trigger_chunk_before_parse_finished_failed(self, api_client, uploaded_document):
        document_id = uploaded_document["documentId"]

        response = api_client.post(f"/api/documents/{document_id}/chunk")

        if response.status_code == 202:
            body = assert_success_response(response)
            assert body["data"]["documentId"] == document_id
        else:
            assert_http_status(response, 400)
            assert_error_response(response, expected_code=40008)