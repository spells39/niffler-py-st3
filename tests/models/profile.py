from typing import Optional

from pydantic import BaseModel


class ProfilePayload(BaseModel):
    fullname: str
    id: str
    username: str
    photo: Optional[str] = None


class ProfileResp(BaseModel):
    id: str
    username: str
    fullname: str
    currency: str