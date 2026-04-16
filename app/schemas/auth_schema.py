from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class AuthRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    agreement_id: str


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    agreement_id: str
    accepted_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
