from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class CreateTarget(BaseModel):
    username: str
    platform: str
    email: Optional[EmailStr] = None
    phone: str | None = None
    target_url: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def check_empty_str(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def phone_validator(cls, phone: str) -> str | None:
        phone = phone.lstrip('+')
        if phone.isdigit() and 7 <= len(phone) <= 15:
            return phone
        return None


class TargetResponse(BaseModel):
    username: str
    platform: str
    email: EmailStr | None
    phone: str | None
    target_url: str | None


class TargetWithMessageResponse(BaseModel):
    message: str
    target: TargetResponse


class TargetType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"