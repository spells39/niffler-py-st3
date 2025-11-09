from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, Field

BaseAuth = declarative_base()

class OAuthRequest(BaseModel):
    response_type: str = "code"
    client_id: str = "client"
    scope: str = "openid"
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str = "S256"


class User(BaseAuth, SQLModel, table=True):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}

    id: UUID = Field(primary_key=True)
    username: str
    password: str
    enabled: bool
    account_non_expired: bool
    account_non_locked: bool
    credentials_non_expired: bool
