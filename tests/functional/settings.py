from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')
    elastic_host: str = Field(..., env='ELASTIC_HOST')
    elastic_port: int = Field(..., env='ELASTIC_PORT')
    es_index: str = Field(..., env='ELASTIC_INDEX')
    es_id_field: str = 'id'
    service_url: str = Field('http://0.0.0.0:8000', env='SERVICE_URL')
    #es_index_mapping: dict =

    class Config:
        env_file = '.env'


settings = Settings()
