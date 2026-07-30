from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, send_reset_password_email
from app.core.security import create_access_token
from app.models.users import User
from app.schemas.token import Token
from app.schemas.users import UserCreate, UserResponse
from app.services import user as user_service
from app.core.security import create_reset_password_token, verify_reset_password_token, hash_password
from app.schemas.password_reset import ResetPasswordRequest, ResetPasswordResponse, ForgotPasswordRequest


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_service.get_user(
        db=db, identifier=user_in.email
    )

    if existing_user:
        if existing_user.email == user_in.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        if existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )

    try:
        return await user_service.create_user(db=db, new_user=user_in)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await user_service.authenticate_user(
        db=db,
        username_or_email=form_data.username,
        password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
        request: ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user(db=db, identifier=request.email)
    if user:
        reset_token = create_reset_password_token(email=user.email)
        background_tasks.add_task(
            send_reset_password_email,
            email_to=user.email,
            token=reset_token,
        )
    return {"message": "Password reset email sent"}


@router.post("/reset-password", response_model=ResetPasswordResponse, status_code=status.HTTP_202_ACCEPTED)
async def reset_password(request: ResetPasswordRequest,
                         db: AsyncSession = Depends(get_db)
    ):
    email: str = verify_reset_password_token(request.token)
    user = await user_service.get_user(db=db, identifier=email)
    if user:
        hashed_password = hash_password(request.new_password)
        user.hashed_password = hashed_password
        await db.commit()
        return {"message": "Password was reset"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
