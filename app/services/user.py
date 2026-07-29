from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import hash_password


async def get_user_by_email_or_username(db: AsyncSession, email: str, username: str) -> User | None:
    stmt = select(User).where(User.email == email, User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, new_user: UserCreate) -> User:
    hashed_pwd = hash_password(new_user.password)
    db_user = User(
        email=new_user.email,
        username=new_user.username,
        hashed_password=hashed_pwd,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user