def assert_http_status(response, expected_status):
    assert response.status_code == expected_status, (
        f"HTTP 状态码错误，期望 {expected_status}，实际 {response.status_code}，响应：{response.text}"
    )

def assert_success_response(response):
    body = response.json()

    assert body["code"] == 0
    assert body["message"] == "success"
    assert "timestamp" in body
    assert "requestId" in body

    return body

def assert_error_response(response, expected_code=None):
    body = response.json()

    assert body["code"] != 0
    assert body["message"]
    assert "timestamp" in body

    if expected_code is not None:
        assert body["code"] == expected_code

    return body