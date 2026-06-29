import os
import yaml

from pathlib import Path

class Config:
    def __init__(self):
        env = os.getenv('TEST_ENV', 'local')
        config_path = Path(__file__).resolve().parents[1] / "config" / f"{env}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with config_path.open("r", encoding="utf-8") as file:
            self._config = yaml.safe_load(file)

    @property
    def base_url(self):
        return self._config["base_url"].rstrip("/")

    @property
    def timeout(self):
        return self._config.get("timeout", 10)

    @property
    def headers(self):
        return self._config.get("headers", {})