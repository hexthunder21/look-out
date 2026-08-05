from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette import status
from app.schemas.targets import CreateTarget, TargetResponse, TargetWithMessageResponse
from app.api.deps import TargetParamsDep, CurrentUserDep, DBSessionDep
from app.models.targets import Target


router = APIRouter()


@router.post("/add-target", response_model=TargetWithMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_target(
        target: CreateTarget,
        current_user: CurrentUserDep,
        db: DBSessionDep
        ):
    new_target = Target(**target.model_dump(), user_id=current_user.id)
    db.add(new_target)
    await db.commit()
    await db.refresh(new_target)
    return {"message": "Target added!"}


@router.get("/get-targets", response_model=List[TargetResponse], status_code=status.HTTP_200_OK)
async def get_targets(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        pagination_params: TargetParamsDep
    ):
    query = (
        select(Target).where(Target.user_id == current_user.id)
        .limit(pagination_params.limit)
        .offset(pagination_params.offset)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/get-target/{target}", response_model=TargetResponse, status_code=status.HTTP_200_OK)
async def get_target(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        target: str
        ):
    query = select(Target).where(Target.user_id == current_user.id,
                                 Target.username == target)
    result = await db.execute(query)
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or invalid credential!"
            )
    
    return target