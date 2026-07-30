from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.schemas.targets import CreateTarget, TargetWithMessageResponse
from app.api.deps import get_current_user, get_db
from app.models.targets import Target
from app.models.users import User
from app.services import user as user_service


router = APIRouter()


@router.post("/add_target", response_model=TargetWithMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_target(
        target: CreateTarget,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
        ):
    new_target = Target(**target.model_dump(), user_id=current_user.id)
    db.add(new_target)
    await db.commit()
    await db.refresh(new_target)
    return {"message": "Target added ->"}

