from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# from tests.functional.testdata.elastic_mapping import ELASTICSEARCH_SCHEMA

BASE_DIR = Path(__file__).parent


class TestSettings(BaseSettings):
    elastic_host: str = Field('127.0.0.1', validation_alias='ELASTIC_HOST')
    print(elastic_host)
    elastic_port: int = Field(9200, validation_alias='ELASTIC_PORT')
    elastic_user: str | None = Field(None, validation_alias='ELASTIC_USER')
    elastic_password: SecretStr | None = Field(None, validation_alias='ELASTIC_PASSWORD')
    redis_host: str = Field('127.0.0.1', validation_alias='REDIS_HOST')
    redis_port: int = Field(6379, validation_alias='REDIS_PORT')
    redis_password: SecretStr | None = Field(None, validation_alias='REDIS_PASSWORD')
    redis_db: int = Field(0, validation_alias='REDIS_DB')

    service_url: str = Field(validation_alias='SERVICE_URL')

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    def get_elastic_url(self) -> str:
        auth_part = f"{self.elastic_user}:{self.elastic_password.get_secret_value()}@" if self.elastic_user and self.elastic_password else ""
        return f"http://{auth_part}{self.elastic_host}:{self.elastic_port}"

    def get_redis_url(self) -> str:
        auth_part = f":{self.redis_password.get_secret_value()}@" if self.redis_password else ""
        return f"redis://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def es_url_to_connect(self):
        return f"http://{self.elastic_host}:{self.elastic_port}"


test_settings = TestSettings()
