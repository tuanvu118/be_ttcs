from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict


class DonViBase(BaseModel):
    ten: str
    logo: Optional[str] = None
    loai: Optional[str] = None


class DonViCreate(DonViBase):
    pass


class DonViUpdate(BaseModel):
    ten: Optional[str] = None
    logo: Optional[str] = None
    loai: Optional[str] = None


class DonViRead(DonViBase):
    id: PydanticObjectId

    model_config = ConfigDict(from_attributes=True)

