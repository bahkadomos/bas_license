import os
from typing import Annotated

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums import CaptchaService


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    debug: Annotated[bool, Field(alias="DEBUG")]

    postgres_user: Annotated[str, Field(alias="POSTGRES_USER")]
    postgres_password: Annotated[str, Field(alias="POSTGRES_PASSWORD")]
    postgres_host: Annotated[str, Field(alias="POSTGRES_HOST")]
    postgres_port: Annotated[str, Field(alias="POSTGRES_PORT")]
    postgres_db: Annotated[str, Field(alias="POSTGRES_DB")]

    private_key: Annotated[str, Field(alias="PRIVATE_KEY")]

    bas_username: Annotated[str, Field(alias="BAS_USERNAME")]
    bas_password: Annotated[str, Field(alias="BAS_PASSWORD")]

    captcha_service: Annotated[
        CaptchaService, Field(default=CaptchaService.capmonster)
    ]
    capguru_key: Annotated[str, Field(alias="CAPGURU_KEY")]
    capmonster_key: Annotated[str, Field(alias="CAPMONSTER_KEY")]
    captcha_attempts: Annotated[int, Field(default=60)]
    captcha_delay: Annotated[int, Field(default=2)]

    @computed_field # type: ignore[misc]
    @property
    def dsn(self) -> str:
        return ("postgresql+asyncpg://"
                f"{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}"
                f"/{self.postgres_db}")


settings = Settings()
