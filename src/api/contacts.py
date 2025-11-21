from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from src.database.db import get_db
from src.schemas import (
    ContactResponse,
    ContactModel,
    ContactShortResponse,
    ContactUpdate,
)
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactShortResponse])
async def get_contacts(
    page: int = 1,
    show: int = 10,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        page,
        show,
        filter={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        },
    )
    return contacts


@router.get("{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("", response_model=ContactResponse)
async def create_contact(contact: ContactModel, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    try:
        return await contact_service.create_contact(contact)
    except IntegrityError as e:
        if "contacts_email_key" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact with this email already exists",
            )
        elif "contacts_phone_key" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact with this phone number already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create contact"
        )


@router.patch("{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int, contact: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    updated_contact = await contact_service.update_contact(contact_id, contact)
    if not updated_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return updated_contact


@router.delete("{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    deleted_contact = await contact_service.delete_contact(contact_id)
    if deleted_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return deleted_contact


@router.get("/birthdays/upcoming", response_model=List[ContactShortResponse])
async def get_upcoming_birthdays(
    days_ahead: int = 7, db: AsyncSession = Depends(get_db)
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(days_ahead)
    return contacts
