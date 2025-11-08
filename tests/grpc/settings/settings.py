from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    wiremock_host: str = Field(default="localhost:8094", alias="WIREMOCK_HOST")
    currency_service_host: str = Field(default="localhost:8092", alias="CURRENCY_SERVICE_HOST")