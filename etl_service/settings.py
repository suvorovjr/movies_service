from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgres_')
    host: str = Field(..., alias='SQL_HOST')
    port: int = Field(..., alias='SQL_PORT')
    dbname: str = Field(..., alias='POSTGRES_DB')
    user: str = ...
    password: str = ...

    def get_dsn(self) -> dict:
        return self.model_dump()


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='es_')
    host: str = Field(..., alias='ELASTIC_HOST')
    port: str = Field(..., alias='ELASTIC_PORT')

    def get_host(self):
        return f'http://{self.host}:{self.port}'


class Settings(BaseSettings):
    debug: bool = Field(..., alias='DEBUG')
    database_settings: DatabaseSettings = DatabaseSettings()
    elasticsearch_settings: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()
