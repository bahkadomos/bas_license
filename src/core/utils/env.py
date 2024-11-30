import os

from dotenv import get_key, set_key


class EnvManager:
    def __init__(self):
        self._env_path = os.path.join(os.getcwd(), ".env")

    def get(self, key: str) -> str | None:
        return get_key(self._env_path, key)

    def set(self, key: str, value: str) -> None:
        set_key(self._env_path, key, value)
