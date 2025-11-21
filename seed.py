import asyncio
from datetime import date, timedelta
from faker import Faker
from sqlalchemy import delete, text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.conf.config import config
from src.database.models import Contact

fake = Faker()


async def seed_contacts(session, count: int = 20):
    """Create sample contacts with random data"""
    contacts = []

    for i in range(count):
        # Generate birthdays spread throughout the year
        # Some in the past, some upcoming
        days_offset = fake.random_int(min=-180, max=180)
        birthday = date.today() + timedelta(days=days_offset)
        # Keep only month and day, vary the birth year
        birthday = birthday.replace(year=fake.random_int(min=1950, max=2005))

        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=f"+380{fake.random_number(digits=9, fix_len=True)}",
            birthday=birthday,
            additional_info=fake.text(max_nb_chars=100)
            if fake.boolean(chance_of_getting_true=30)
            else None,
        )
        contacts.append(contact)

    session.add_all(contacts)
    await session.commit()
    print(f"✅ Created {count} contacts")


async def seed_contacts_with_upcoming_birthdays(session, count: int = 5):
    """Create contacts with birthdays in the next 7 days"""
    contacts = []

    for i in range(count):
        # Birthday in next 7 days
        days_ahead = fake.random_int(min=0, max=7)
        upcoming_date = date.today() + timedelta(days=days_ahead)
        # Use random birth year
        birthday = upcoming_date.replace(year=fake.random_int(min=1960, max=2000))

        contact = Contact(
            first_name=f"Upcoming{i + 1}",
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=f"+380{fake.random_number(digits=9, fix_len=True)}",
            birthday=birthday,
            additional_info="Birthday coming soon!",
        )
        contacts.append(contact)

    session.add_all(contacts)
    await session.commit()
    print(f"✅ Created {count} contacts with upcoming birthdays")


async def clear_database(session):
    """Clear all contacts from database"""
    # Use SQLAlchemy delete statement
    stmt = delete(Contact)
    result = await session.execute(stmt)
    await session.commit()
    print(f"🗑️  Cleared {result.rowcount} contacts from database")


async def get_contacts_count(session):
    """Get total number of contacts"""
    stmt = select(Contact)
    result = await session.execute(stmt)
    contacts = result.scalars().all()
    return len(contacts)


async def main():
    # Create async engine
    engine = create_async_engine(config.DB_URL, echo=False)

    # Create session maker
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Optional: Clear existing data
        confirm = input("Do you want to clear existing data? (y/n): ")
        if confirm.lower() == "y":
            await clear_database(session)

        # Seed regular contacts
        await seed_contacts(session, count=20)

        # Seed contacts with upcoming birthdays
        await seed_contacts_with_upcoming_birthdays(session, count=5)

        # Get total count
        total = await get_contacts_count(session)

        print("\n✨ Database seeded successfully!")
        print(f"📊 Total contacts in database: {total}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
