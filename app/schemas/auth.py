from pydantic import BaseModel, EmailStr, SecretStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: SecretStr
    full_name: str = Field(min_length=4, max_length=256)

class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    detail: str