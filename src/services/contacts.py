from typing import List
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def get_contacts(self, page: int, show: int, filter: dict | None = None):
        return await self.contact_repository.get_contacts(page - 1, show, filter)

    async def get_contact(self, contact_id: int):
        return await self.contact_repository.get_contact(contact_id)

    async def create_contact(self, contact: ContactModel):
        return await self.contact_repository.create_contact(contact)

    async def update_contact(self, contact_id: int, contact: ContactUpdate):
        return await self.contact_repository.update_contact(contact_id, contact)

    async def delete_contact(self, contact_id: int):
        return await self.contact_repository.delete_contact(contact_id)

    async def get_upcoming_birthdays(self, days_ahead: int = 7) -> List[Contact]:
        today = date.today()
        return await self.contact_repository.get_contacts_with_birthday_in_period(
            today, today + timedelta(days=days_ahead)
        )
