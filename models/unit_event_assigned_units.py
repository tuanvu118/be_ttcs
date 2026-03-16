from beanie import Document, PydanticObjectId

class UnitEventAssignedUnits(Document):
  unitEventId: PydanticObjectId
  unitId: PydanticObjectId

  class Settings:
    name = "unit_event_assigned_units"
