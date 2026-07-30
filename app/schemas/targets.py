from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CreateTarget(BaseModel):
    username: str
    platform: str
    target_url: str


class TargetResponse(BaseModel):
    username: str
    platform: str
    target_url: str


class TargetWithMessageResponse(BaseModel):
    message: str
    # target: TargetResponse