from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CreateTarget(BaseModel):
    username: str
    platform: str
    email: EmailStr | None
    phone: str | None
    target_url: str | None


class TargetResponse(BaseModel):
    username: str
    platform: str
    email: EmailStr | None
    phone: str | None
    target_url: str | None


class TargetWithMessageResponse(BaseModel):
    message: str
    # target: TargetResponse


class TargetType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"