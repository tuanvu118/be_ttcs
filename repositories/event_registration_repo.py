from models.event_registration import EventRegistration


class EventRegistrationRepository:

    @staticmethod
    async def create(data: dict):
        registration = EventRegistration(**data)
        await registration.insert()
        return registration

    @staticmethod
    async def get_by_event_and_user(event_id, user_id):
        return await EventRegistration.find_one(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id
        )

    @staticmethod
    async def get_by_user(user_id):
        return await EventRegistration.find(
            EventRegistration.user_id == user_id
        ).to_list()

    @staticmethod
    async def get_by_event(event_id):
        return await EventRegistration.find(
            EventRegistration.event_id == event_id
        ).to_list()

    @staticmethod
    async def count_by_event(event_id):
        return await EventRegistration.find(
            EventRegistration.event_id == event_id
        ).count()

    @staticmethod
    async def delete_by_event_and_user(event_id, user_id):
        registration = await EventRegistration.find_one(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id
        )

        if not registration:
            return False

        await registration.delete()
        return True