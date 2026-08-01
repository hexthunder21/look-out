from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import hash_password, verify_password


async def get_user(db: AsyncSession, identifier: str) -> User | None:
    stmt = select(User).where(
        or_(
            User.email == identifier,
            User.username == identifier
        )
    )
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


async def authenticate_user(db: AsyncSession, username_or_email: str, password: str) -> User | None:
    user = await get_user(db=db, identifier=username_or_email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_password(db: AsyncSession, identifier: str, new_password: str) -> None:
    user = await get_user(db=db, identifier=identifier)
    user.hashed_password = new_password
    await db.commit()
    await db.refresh(user)

