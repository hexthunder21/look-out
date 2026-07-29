from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.users import UserCreate, UserResponse
from app.services import user as user_service


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_service.get_user_by_email_or_username(
        db, email=user_in.email, username=user_in.username
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    return await user_service.create_user(db=db, new_user=user_in)


