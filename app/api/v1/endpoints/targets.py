from typing import List
from fastapi import APIRouter, HTTPException, Query, Path
from starlette import status
from app.schemas.targets import CreateTarget, TargetResponse, TargetWithMessageResponse
from app.api.deps import TargetParamsDep, CurrentUserDep, DBSessionDep
from app.services.target import TargetService


router = APIRouter()


@router.post("", response_model=TargetWithMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_target(
        target: CreateTarget,
        current_user: CurrentUserDep,
        db: DBSessionDep
        ):
    created_target = await TargetService.create_target(db=db, target=target, user_id=current_user.id)
    return {
        "message": "Target created successfully",
        "target": created_target
    }


@router.get("", response_model=List[TargetResponse])
async def get_targets(
        db: DBSessionDep,
        current_user: CurrentUserDep,
        pagination_params: TargetParamsDep
    ):
    targets = await TargetService.get_targets(
        db=db,
        user_id=current_user.id,
        target_params=pagination_params)

    return targets


@router.get("/{target}", response_model=TargetResponse)
async def get_target(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        target: str = Path(..., description="Email, phone or username to search for")
    ):
    single_target = await TargetService.get_target_by_credential(
        db=db,
        user_id=current_user.id,
        raw_target_data=target
    )

    return single_target


@router.delete("/{target}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
        current_user: CurrentUserDep,
        db: DBSessionDep,
        target: str = Path(..., description="Email, phone or username to search for")
    ):
    await TargetService.delete_target(
        db=db,
        user_id=current_user.id,
        raw_target_data=target
    )
