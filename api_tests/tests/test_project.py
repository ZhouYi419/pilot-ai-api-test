import allure
import pytest

from common.assert_utils import (
    assert_error_response,
    assert_http_status,
    assert_success_response,
)
from data.project_data import (
    build_invalid_project_payload,
    build_project_create_payload,
    build_project_update_payload,
)

@allure.epic("TestPilot AI")
@allure.feature("项目管理")
@pytest.mark.project
class TestProjectApi:

    @allure.story("创建项目")
    @allure.title("创建项目成功")
    @pytest.mark.smoke
    def test_create_project_success(self, api_client):
        payload = build_project_create_payload()

        response = api_client.post("/api/projects", json_body=payload)

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert body["data"]["projectName"] == payload["projectName"]
        assert body["data"]["projectCode"] == payload["projectCode"]
        assert body["data"]["status"] == payload["status"]

        project_id = body["data"]["id"]
        api_client.delete(f"/api/projects/{project_id}")

    @allure.story("创建项目")
    @allure.title("创建项目失败：必填字段为空")
    def test_create_project_required_field_failed(self, api_client):
        response = api_client.post(
            "/api/projects",
            json_body=build_invalid_project_payload(),
        )

        assert_http_status(response, 400)
        assert_error_response(response, expected_code=40000)

    @allure.story("分页查询项目")
    @allure.title("分页查询项目成功")
    def test_query_project_page_success(self, api_client):
        response = api_client.get(
            "/api/projects",
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

    @allure.story("分页查询项目")
    @allure.title("分页查询项目失败：pageNum 小于 1")
    def test_query_project_page_invalid_page_num(self, api_client):
        response = api_client.get(
            "/api/projects",
            params={
                "pageNum": 0,
                "pageSize": 10,
            },
        )

        assert_http_status(response, 400)
        assert_error_response(response, expected_code=40000)

    @allure.story("项目完整流程")
    @allure.title("创建、查询详情、修改、删除项目")
    @pytest.mark.smoke
    def test_project_crud_success(self, api_client):
        create_payload = build_project_create_payload()

        create_response = api_client.post("/api/projects", json_body=create_payload)
        assert_http_status(create_response, 200)
        create_body = assert_success_response(create_response)

        project_id = create_body["data"]["id"]

        try:
            detail_response = api_client.get(f"/api/projects/{project_id}")
            assert_http_status(detail_response, 200)
            detail_body = assert_success_response(detail_response)
            assert detail_body["data"]["id"] == project_id

            update_payload = build_project_update_payload()
            update_response = api_client.put(
                f"/api/projects/{project_id}",
                json_body=update_payload,
            )
            assert_http_status(update_response, 200)
            update_body = assert_success_response(update_response)
            assert update_body["data"]["projectName"] == update_payload["projectName"]

            delete_response = api_client.delete(f"/api/projects/{project_id}")
            assert_http_status(delete_response, 200)
            assert_success_response(delete_response)

            get_deleted_response = api_client.get(f"/api/projects/{project_id}")
            assert_http_status(get_deleted_response, 404)
            assert_error_response(get_deleted_response, expected_code=40401)

        finally:
            api_client.delete(f"/api/projects/{project_id}")