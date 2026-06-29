import allure
import pytest

from common.assert_utils import assert_http_status, assert_success_response


@allure.epic("TestPilot AI")
@allure.feature("系统管理")
@pytest.mark.system
class TestSystemApi:
    @allure.story("系统连通性测试")
    @allure.title("GET /api/system/ping 返回 pong")
    @pytest.mark.smoke
    def test_ping_success(self, api_client):
        response = api_client.get("/api/system/ping")

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert body["data"]["application"] == "testpilot-ai"
        assert body["data"]["message"] == "pong"

    @allure.story("基础设施健康检查")
    @allure.title("GET /api/system/health 返回健康检查结果")
    def test_health_success(self, api_client):
        response = api_client.get("/api/system/health")

        assert_http_status(response, 200)
        body = assert_success_response(response)

        assert isinstance(body["data"], dict)