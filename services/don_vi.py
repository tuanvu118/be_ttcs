from typing import List

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from models.don_vi import DonVi
from repositories.don_vi_repo import DonViRepo
from schemas.don_vi import DonViCreate, DonViRead, DonViUpdate


class DonViService:
    def __init__(self, repo: DonViRepo) -> None:
        self.repo = repo

    async def create_don_vi(self, payload: DonViCreate) -> DonViRead:
        don_vi = DonVi(
            ten=payload.ten,
            logo=payload.logo,
            loai=payload.loai,
        )
        saved = await self.repo.create(don_vi)
        return DonViRead.model_validate(saved)

    async def get_don_vi(self, don_vi_id: PydanticObjectId) -> DonViRead:
        don_vi = await self.repo.get_by_id(don_vi_id)
        if not don_vi:
            app_exception(ErrorCode.DONVI_NOT_FOUND)
        return DonViRead.model_validate(don_vi)

    async def list_don_vi(self) -> List[DonViRead]:
        items = await self.repo.list_all()
        return [DonViRead.model_validate(dv) for dv in items]

    async def update_don_vi(
        self, don_vi_id: PydanticObjectId, payload: DonViUpdate
    ) -> DonViRead:
        don_vi = await self.repo.get_by_id(don_vi_id)
        if not don_vi:
            app_exception(ErrorCode.DONVI_NOT_FOUND)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(don_vi, field, value)

        saved = await self.repo.update(don_vi)
        return DonViRead.model_validate(saved)

    async def delete_don_vi(self, don_vi_id: PydanticObjectId) -> None:
        don_vi = await self.repo.get_by_id(don_vi_id)
        if not don_vi:
            app_exception(ErrorCode.DONVI_NOT_FOUND)
        await self.repo.delete(don_vi)

