from typing import List, Optional

from beanie import PydanticObjectId

from models.don_vi import DonVi


class DonViRepo:
    async def create(self, don_vi: DonVi) -> DonVi:
        return await don_vi.insert()

    async def get_by_id(self, don_vi_id: PydanticObjectId) -> Optional[DonVi]:
        return await DonVi.get(don_vi_id)

    async def list_all(self) -> List[DonVi]:
        return await DonVi.find_all().to_list()

    async def delete(self, don_vi: DonVi) -> None:
        await don_vi.delete()

    async def update(self, don_vi: DonVi) -> DonVi:
        return await don_vi.save()

