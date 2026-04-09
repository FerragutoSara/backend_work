from pydantic import BaseModel, EmailStr


class AuthRegister(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    privacy_level: int


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    id: str
    name: str
    surname: str
    email: EmailStr
    privacy_level: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
