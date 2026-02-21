import asyncio

from database.models import Organization, User
from database.session import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select


async def fix_missing_orgs():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Get all users without organizations
        stmt = select(User).options(selectinload(User.organization))
        result = await session.execute(stmt)
        users = result.scalars().all()

        count = 0
        for user in users:
            if not user.organization and not user.organization_id:
                print(f"Fixing user {user.email}...")
                org_name = f"{user.email}'s Org"

                # Check if org name exists just in case
                existing_org_stmt = select(Organization).where(
                    Organization.name == org_name
                )
                existing_org = (
                    await session.execute(existing_org_stmt)
                ).scalar_one_or_none()

                if existing_org:
                    new_org = existing_org
                else:
                    new_org = Organization(name=org_name, credits=10.0)
                    session.add(new_org)
                    await session.commit()
                    await session.refresh(new_org)

                user.organization_id = new_org.id
                session.add(user)
                count += 1

        await session.commit()
        print(f"Fixed {count} users.")


def main():
    asyncio.run(fix_missing_orgs())


if __name__ == "__main__":
    main()
