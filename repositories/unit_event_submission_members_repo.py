from models.unit_event_submission_members import UnitEventSubmissionMember
from beanie import PydanticObjectId
from typing import Optional, List


class UnitEventSubmissionMembersRepo:
    async def create(self, unit_event_submission_member: UnitEventSubmissionMember) -> UnitEventSubmissionMember:
        return await unit_event_submission_member.insert()
    
    async def get_by_id(self, unit_event_submission_member_id: PydanticObjectId) -> Optional[UnitEventSubmissionMember]:
        return await UnitEventSubmissionMember.get(unit_event_submission_member_id)

    async def update_check_in(self, unit_event_submission_member_id: PydanticObjectId, check_in: bool) -> UnitEventSubmissionMember:
        unit_event_submission_member = await self.get_by_id(unit_event_submission_member_id)
        unit_event_submission_member.checkIn = check_in
        return await unit_event_submission_member.save()

    async def get_all_by_unit_event_submission_id(self, unit_event_submission_id: PydanticObjectId) -> List[UnitEventSubmissionMember]:
        return await UnitEventSubmissionMember.find(UnitEventSubmissionMember.unitEventSubmissionId == unit_event_submission_id).to_list()

    async def delete_all_by_unit_event_submission_id(
        self, unit_event_submission_id: PydanticObjectId
    ) -> None:
        members = await self.get_all_by_unit_event_submission_id(unit_event_submission_id)
        for member in members:
            await member.delete()