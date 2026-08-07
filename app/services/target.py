from typing import List
from fastapi import HTTPException
from starlette import status
from sqlalchemy import select, delete, update
from app.models.targets import Target
from app.schemas.targets import TargetType, CreateTarget
from app.api.deps import TargetParamsDep, CurrentUserDep, DBSessionDep
import re

TARGET_MAP = {
    TargetType.USERNAME: Target.username,
    TargetType.EMAIL: Target.email,
    TargetType.PHONE: Target.phone
}

class TargetService:
    @staticmethod
    async def parse_target_credentials(credential: str) -> tuple[TargetType, str]:
        cred = credential.strip()

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.match(email_pattern, cred):
            return TargetType.EMAIL, cred

        phone = cred.lstrip('+')
        if phone.isdigit() and 7 <= len(phone) <= 15:
            return TargetType.PHONE, cred

        username = cred.lstrip('@')
        if username:
            return TargetType.USERNAME, username

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect credentials or target not found")


    @classmethod
    async def create_target(
            cls,
            target: CreateTarget,
            user_id: int,
            db: DBSessionDep
    ) -> Target:
        new_target = Target(**target.model_dump(), user_id=user_id)
        db.add(new_target)
        await db.commit()
        await db.refresh(new_target)
        return new_target


    @classmethod
    async def get_targets(
            cls,
            user_id: int,
            db: DBSessionDep,
            target_params: TargetParamsDep
    ) -> List[Target]:
        query = (
            select(Target).where(Target.user_id == user_id)
            .limit(target_params.limit)
            .offset(target_params.offset)
        )
        results = await db.execute(query)

        return list(results.scalars().all())


    @classmethod
    async def get_target_by_credential(
            cls,
            user_id: int,
            db: DBSessionDep,
            raw_target_data: str
    ) -> Target | None:
        data_type, credential = await cls.parse_target_credentials(raw_target_data)
        field = TARGET_MAP.get(data_type)

        if field is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid target type or format")

        query = select(Target).where(Target.user_id == user_id, field == credential)
        result = await db.execute(query)
        target_obj = result.scalar_one_or_none()

        if not target_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target not found."
                )

        return target_obj
