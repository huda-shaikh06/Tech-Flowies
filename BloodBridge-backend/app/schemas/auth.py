from typing import Optional
from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number, e.g. 3001234567")
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    city: Optional[str] = "Karachi"


class LoginRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number, e.g. 3001234567")
    password: str = Field(..., min_length=6)


class UserProfile(BaseModel):
    id: str
    phone: str
    name: str
    city: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
