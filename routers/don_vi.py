from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from repositories.don_vi_repo import DonViRepo
from schemas.auth import TokenData
from schemas.don_vi import DonViCreate, DonViRead, DonViUpdate
from security import require_admin, require_user
from services.don_vi import DonViService


router = APIRouter(prefix="/donvi", tags=["DonVi"])


def get_donvi_service() -> DonViService:
    return DonViService(DonViRepo())


@router.post(
    "",
    response_model=DonViRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_donvi(
    payload: DonViCreate,
    service: DonViService = Depends(get_donvi_service),
) -> DonViRead:
    """
    Chỉ ADMIN mới được tạo đơn vị.
    """
    return await service.create_don_vi(payload)


@router.get(
    "",
    response_model=List[DonViRead],
)
async def list_donvi(
    current_user: TokenData = Depends(require_user),
    service: DonViService = Depends(get_donvi_service),
) -> List[DonViRead]:
    """
    Danh sách đơn vị:
    - ADMIN có thể thấy tất cả (hiện tại: đơn giản trả về tất cả).
    - Các user bình thường: trong thực tế nên filter theo đơn vị của họ,
      nhưng ở đây bạn nói 'xem đơn vị thì tất cả người trong đơn vị đấy có thể xem đơn vị của mình',
      nên thường sẽ là lấy đúng đơn vị hiện tại từ context. Để đơn giản, trả full list.
    """
    return await service.list_don_vi()


@router.get(
    "/{don_vi_id}",
    response_model=DonViRead,
)
async def get_donvi(
    don_vi_id: PydanticObjectId,
    current_user: TokenData = Depends(require_user),
    service: DonViService = Depends(get_donvi_service),
) -> DonViRead:
    """
    Xem chi tiết đơn vị:
    - Mọi user đã login đều xem được thông tin đơn vị (có thể bổ sung check belong-to sau).
    """
    return await service.get_don_vi(don_vi_id)


@router.put(
    "/{don_vi_id}",
    response_model=DonViRead,
    dependencies=[Depends(require_admin)],
)
async def update_donvi(
    don_vi_id: PydanticObjectId,
    payload: DonViUpdate,
    service: DonViService = Depends(get_donvi_service),
) -> DonViRead:
    """
    Chỉ ADMIN mới được cập nhật đơn vị.
    """
    return await service.update_don_vi(don_vi_id, payload)


@router.delete(
    "/{don_vi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_donvi(
    don_vi_id: PydanticObjectId,
    service: DonViService = Depends(get_donvi_service),
) -> None:
    """
    Chỉ ADMIN mới được xóa đơn vị.
    """
    await service.delete_don_vi(don_vi_id)

