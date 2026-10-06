from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field
from src.auth.constants import UserRole

EmailType = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Email address"
    )
]


class RegisterIn(BaseModel):
    email: EmailType
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.OWNER


class LoginIn(BaseModel):
    email: EmailType
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailType
    full_name: Optional[str] = None
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdateIn(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class ResetPasswordIn(BaseModel):
    email: EmailType
    reset_secret_key: str
    new_password: str = Field(..., min_length=6)

