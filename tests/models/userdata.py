from datetime import date

from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, Field

BaseUserData = declarative_base()

class User(BaseUserData, SQLModel, table=True):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'public'}

    id: str = Field(primary_key=True, default=None)
    username: str
    currency: str = "USD"
    firstname: str | None = None
    surname: str | None = None
    photo: str | None = None
    photo_small: str | None = None
    full_name: str | None = None


class UserName(BaseModel):
    username: str


class Friendship(SQLModel, table=True):
    __tablename__ = 'friendship'
    requester_id: str = Field(primary_key=True, foreign_key="user.id")
    addressee_id: str = Field(primary_key=True, foreign_key="user.id")
    status: str
    created_date: date
