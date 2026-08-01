from typing import AsyncGenerator, Annotated
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.users import User
from app.services.user import get_user
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


# =======================================================
class PaginationTargetParams(BaseModel):
    limit: int = Field(5, ge=1, lt=10, description="Limit the number of results")
    offset: int = Field(0, ge=0, description="Offset for the results")


TargetParamsDep = Annotated[PaginationTargetParams, Depends()]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
# =======================================================