from fastapi import HTTPException
from starlette import status
from app.models.targets import Target
from app.schemas.targets import TargetType
import re

TARGET_MAP = {
    TargetType.USERNAME: Target.username,
    TargetType.EMAIL: Target.email,
    TargetType.PHONE: Target.phone
}

async def parse_target_credentials(credential: str) -> tuple[TargetType, str]:
    cred = credential.strip()

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.match(email_pattern, cred):
        return TargetType.EMAIL, cred

    phone = cred.lstrip('+')
    if phone.isdigit() and 7 <= len(phone) <= 15:
        return TargetType.PHONE, cred
    
    username = cred.lstrip('@')
    if username:
        return TargetType.USERNAME, username

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials or target not found")

