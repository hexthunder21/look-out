from typing import AsyncGenerator, Annotated
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import MessageSchema, MessageType, FastMail
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.users import User
from app.services.user import get_user
from app.services.email import conf
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_credential: str = payload.get("sub")
        if user_credential is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user(db=db, identifier=user_credential)
    if user is None:
        raise credentials_exception
    return user


async def send_reset_password_email(email_to: EmailStr, token: str) -> None:
    forget_url_link = f"{settings.APP_HOST}{settings.FORGET_PASS_URL}/{token}"
    html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Password Recovery</h2>
                <p>You have requested a password reset for your account.</p>
                <p>To change your password, click the link below (the link is valid for 15 minutes):</p>
                <p>
                    <a href="{forget_url_link}"
                       style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                       Change Password
                    </a>
                </p>
                <p>Or copy this link into your browser:</p>
                <p><a href="{forget_url_link}">{forget_url_link}</a></p>
                <br>
                <p><small>If you did not request a password reset, simply ignore this email.</small></p>
            </body>
        </html>
        """

    message = MessageSchema(
        subject="Password reset email",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

# =======================================================
class PaginationTargetParams(BaseModel):
    limit: int = Field(5, ge=1, lt=10, description="Limit the number of results")
    offset: int = Field(0, ge=0, description="Offset for the results")


TargetParamsDep = Annotated[PaginationTargetParams, Depends()]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
# =======================================================