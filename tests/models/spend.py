from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    username: str
    archived: bool

    spends: list["Spend"] = Relationship(back_populates="category")


class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    description: str
    category: Category
    spend_date: str
    currency: str
    username: str

    category_id: UUID = Field(foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="spends")


class SpendResp(SQLModel):
    id: str
    spendDate: datetime
    currency: str
    amount: float
    description: str
    username: str
    category: Category


class SpendAdd(BaseModel):
    amount: float
    description: str
    category: dict
    spendDate: str
    currency: str
    id: Optional[str] = None


class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    username: str
    password: str
    enabled: bool
    account_non_expired: bool
    account_non_locked: bool
    credentials_non_expired: bool