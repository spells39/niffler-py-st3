from pydantic import BaseModel


class Envs(BaseModel):
    front_url: str
    api_url: str
    auth_url: str
    auth_secret: str
    spend_db_url: str
    auth_db_url: str
    test_username: str
    test_password: str