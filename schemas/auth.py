from typing import List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class DonViRole(BaseModel):
    don_vi_id: str
    roles: List[str]


class TokenData(BaseModel):
    sub: str
    email: str
    is_active: bool
    roles: List[DonViRole]

