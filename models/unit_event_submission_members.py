from beanie import Document, PydanticObjectId

class UnitEventSubmissionMember(Document):
  unitEventSubmissionId: PydanticObjectId
  userId: PydanticObjectId
  checkIn: bool = False

  class Settings:
    name = "unit_event_submission_members"