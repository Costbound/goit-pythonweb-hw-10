from typing import List
from datetime import date

from sqlalchemy import Integer, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_contacts(
        self, skip: int, limit: int, filter: dict | None = None
    ) -> List[Contact]:
        stmt = select(Contact)

        if filter:
            conditions = []
            if filter.get("first_name"):
                conditions.append(Contact.first_name.ilike(f"%{filter['first_name']}%"))
            if filter.get("last_name"):
                conditions.append(Contact.last_name.ilike(f"%{filter['last_name']}%"))
            if filter.get("email"):
                conditions.append(Contact.email == filter["email"])

            if conditions:
                stmt = stmt.where(and_(*conditions))
            print(conditions)

        stmt = stmt.offset(skip).limit(limit)

        from sqlalchemy.dialects import postgresql

        compiled = stmt.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
        print(f"DEBUG - SQL with values: {compiled}")

        contacts = await self.db.execute(stmt)
        result = list(contacts.scalars().all())
        print(result)
        return result

    async def get_contact(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactModel) -> Contact:
        new_contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return new_contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate
    ) -> Contact | None:
        contact = await self.get_contact(contact_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            self.db.add(contact)
            await self.db.commit()
            await self.db.refresh(contact)
            return contact
        return contact

    async def delete_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
            return contact
        return contact

    async def get_contacts_with_birthday_in_period(
        self, start_date: date, end_date: date
    ) -> List[Contact]:
        """Get contacts who will have a birthday between two dates"""

        stmt = select(Contact).where(
            Contact.birthday.isnot(None),
            cast(func.extract("year", func.age(start_date, Contact.birthday)), Integer)
            != cast(
                func.extract("year", func.age(end_date, Contact.birthday)), Integer
            ),
        )

        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())
