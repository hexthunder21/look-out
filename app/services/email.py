from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from pydantic import EmailStr
from app.core.config import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_FOLDER = BASE_DIR / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)


async def send_reset_password_email(email_to: EmailStr, token: str) -> None:
    forget_url_link = f"{settings.APP_HOST}{settings.FORGET_PASS_URL}/{token}"

    message = MessageSchema(
        subject="Password reset email",
        recipients=[email_to],
        template_body={
            "forget_url_link": forget_url_link,
            "expire_minutes": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES
        },
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="send_email_password_reset.html")