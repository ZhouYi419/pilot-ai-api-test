import pytest

from common.config import Config
from common.http_client import HttpClient

@pytest.fixture(scope="session")
def config():
    return Config()

@pytest.fixture(scope="session")
def api_client(config):
    return HttpClient(
        base_url=config.base_url,
        timeout=config.timeout,
        headers=config.headers,
    )