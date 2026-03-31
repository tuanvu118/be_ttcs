from enum import Enum
from typing import Optional

from beanie import Document


class UnitType(str, Enum):
    LCK = "LCK"
    CLB = "CLB"
    SYSTEM = "SYSTEM"


class Unit(Document):
    name: str
    logo: Optional[str] = None
    introduction: Optional[str] = None
    type: UnitType = UnitType.CLB

    class Settings:
        name = "units"
