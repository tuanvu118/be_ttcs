from enum import Enum
from typing import Optional

from beanie import Document


class DonViType(str, Enum):
    LCK = "LCK"
    CLB = "CLB"
    SYSTEM = "SYSTEM"


class DonVi(Document):
    ten: str
    logo: Optional[str] = None
    loai: DonViType = DonViType.CLB

    class Settings:
        name = "don_vi"
