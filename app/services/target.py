from fastapi import HTTPException
from starlette import status
from app.schemas.targets import TargetType
import re


async def parse_target_credentials(credential: str) -> tuple[TargetType, str]:
    cred = credential.strip()
    username = cred.lstrip('@')
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email = re.match(email_pattern, cred)
    phone = cred.lstrip('+')

    if username:
        return TargetType.USERNAME, username

    if email:
        return TargetType.EMAIL, email.string

    if phone.isdigit() and len(phone) <= 15:
        return TargetType.PHONE, cred

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials or target not found")

