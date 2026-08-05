from typing import List
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, delete, update
from starlette import status
from app.schemas.targets import CreateTarget, TargetResponse, TargetWithMessageResponse, TargetType
from app.api.deps import TargetParamsDep, CurrentUserDep, DBSessionDep
from app.models.targets import Target
from app.services.target import parse_target_credentials, TARGET_MAP


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


@router.get("/get-target", response_model=TargetResponse)
async def get_target(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        target: str = Query(..., description="Email, phone or username to search for")
        ):
    data_type, credential = await parse_target_credentials(target)
    field = TARGET_MAP.get(data_type)

    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid target type or format")

    query = select(Target).where(Target.user_id == current_user.id, field == credential)
    result = await db.execute(query)
    target_obj = result.scalar_one_or_none()

    if not target_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found."
            )

    return target_obj


@router.delete("/del-target", response_model=TargetWithMessageResponse)
async def delete_target(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        target: str = Query(..., description="Email, phone or username to search for")
        ):
    data_type, credential = await parse_target_credentials(target)
    field = TARGET_MAP.get(data_type)

    if field is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target type or format")

    query = delete(Target).where(Target.user_id == current_user.id, field == credential)
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    return {"message": "Target deleted successfully"}

