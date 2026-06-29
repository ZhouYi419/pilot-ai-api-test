import allure
import pytest

from common.assert_utils import (
    assert_error_response,
    assert_http_status,
    assert_success_response,
)
from data.module_data import build_invalid_module_payload, build_module_create_payload
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

@allure.epic("TestPilot AI")
@allure.feature("项目功能模块管理")
@pytest.mark.module
class TestModuleApi:

    @allure.story("创建功能模块")
    @allure.title("在项目下创建模块成功")
    @pytest.mark.smoke
    def test_create_module_success(self, api_client, created_project):
        payload = build_module_create_payload()

        response = api_client.post(
            f"/api/projects/{created_project}/modules",
            json_body=payload,
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert body["data"]["moduleName"] == payload["moduleName"]
        assert body["data"]["moduleCode"] == payload["moduleCode"]
        assert body["data"]["status"] == payload["status"]

    @allure.story("创建功能模块")
    @allure.title("创建模块失败：必填字段为空")
    def test_create_module_required_field_failed(self, api_client, created_project):
        response = api_client.post(
            f"/api/projects/{created_project}/modules",
            json_body=build_invalid_module_payload(),
        )

        assert_http_status(response, 400)
        assert_error_response(response, expected_code=40000)

    @allure.story("分页查询项目功能模块")
    @allure.title("分页查询项目模块成功")
    def test_query_module_page_success(self, api_client, created_project):
        response = api_client.get(
            f"/api/projects/{created_project}/modules",
            params={
                "pageNum": 1,
                "pageSize": 10,
            },
        )

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert "records" in body["data"]
        assert "total" in body["data"]
        assert "pageNum" in body["data"]
        assert "pageSize" in body["data"]

    @allure.story("分页查询项目功能模块")
    @allure.title("分页查询模块失败：项目 ID 不存在")
    def test_query_module_project_not_found(self, api_client):
        response = api_client.get(
            "/api/projects/999999999/modules",
            params={
                "pageNum": 1,
                "pageSize": 10,
            },
        )

        assert_http_status(response, 404)
        assert_error_response(response, expected_code=40401)