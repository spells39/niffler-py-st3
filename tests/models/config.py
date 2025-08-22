from pydantic import BaseModel


class Envs(BaseModel):
    front_url: str
    api_url: str
    spend_db_url: str
    auth_db_url: str
    test_username: str
    test_password: str