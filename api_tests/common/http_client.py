import json

import allure
import requests

class HttpClient:
    def __init__(self, base_url, timeout=10, headers=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(headers or {})

    def get(self, path, params=None, **kwargs):
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path, json_body=None, **kwargs):
        return self._request("POST", path, json=json_body, **kwargs)

    def post_multipart(self, path, files=None, data=None, **kwargs):
        return self._request(
            "POST",
            path,
            files=files,
            data=data,
            **kwargs,
        )

    def put(self, path, json_body=None, **kwargs):
        return self._request("PUT", path, json=json_body, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, **kwargs)
            self._attach_request(method, url, kwargs)
            self._attach_response(response)
            return response

    @staticmethod
    def _attach_request(method, url, kwargs):
        request_info = {
            "method": method,
            "url": url,
            "params": kwargs.get("params"),
            "json": kwargs.get("json"),
            "data": kwargs.get("data"),
            "files": list(kwargs.get("files", {}).keys()) if kwargs.get("files") else None,
        }
        allure.attach(
            json.dumps(request_info, ensure_ascii=False, indent=2),
            name="request",
            attachment_type=allure.attachment_type.JSON,
        )

    @staticmethod
    def _attach_response(response):
        try:
            body = response.json()
            content = json.dumps(body, ensure_ascii=False, indent=2)
            attachment_type = allure.attachment_type.JSON
        except ValueError:
            content = response.text
            attachment_type = allure.attachment_type.TEXT

        allure.attach(
            content,
            name=f"response-{response.status_code}",
            attachment_type=attachment_type,
        )