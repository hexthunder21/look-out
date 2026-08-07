from typing import List
from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import select, delete, update
from starlette import status
from app.schemas.targets import CreateTarget, TargetResponse, TargetWithMessageResponse, TargetType
from app.api.deps import TargetParamsDep, CurrentUserDep, DBSessionDep
from app.services.target import TARGET_MAP
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
        target: str = Path(..., description="Target credential")
    ):
    single_target = await TargetService.get_target_by_credential(
        db=db,
        user_id=current_user.id,
        raw_target_data=target
    )

    return single_target



# @router.get("/get-target", response_model=TargetResponse)
# async def get_target(
#         current_user: CurrentUserDep,
#         db: DBSessionDep,
#         target: str = Query(..., description="Email, phone or username to search for")
#         ):
#     data_type, credential = await parse_target_credentials(target)
#     field = TARGET_MAP.get(data_type)
#
#     if field is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid target type or format")
#
#     query = select(Target).where(Target.user_id == current_user.id, field == credential)
#     result = await db.execute(query)
#     target_obj = result.scalar_one_or_none()
#
#     if not target_obj:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Target not found."
#             )
#
#     return target_obj
#
#
# @router.delete("/del-target", response_model=TargetWithMessageResponse)
# async def delete_target(
#         current_user: CurrentUserDep,
#         db: DBSessionDep,
#         target: str = Query(..., description="Email, phone or username to search for")
#         ):
#     data_type, credential = await parse_target_credentials(target)
#     field = TARGET_MAP.get(data_type)
#
#     if field is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target type or format")
#
#     query = delete(Target).where(Target.user_id == current_user.id, field == credential)
#     result = await db.execute(query)
#     await db.commit()
#
#     if result.rowcount == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
#
#     return {"message": "Target deleted successfully"}

