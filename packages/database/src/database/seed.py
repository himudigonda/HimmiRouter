import asyncio

from database.models import Company, Model, ModelProviderMapping, Provider
from database.session import engine
from sqlmodel import Session, select


async def seed_data():
    async with engine.begin() as conn:
        # Simple sync-style session for seeding
        from sqlalchemy.orm import Session as SyncSession

        def sync_seed(connection):
            from sqlalchemy.orm import Session as SyncSession

            with SyncSession(bind=connection) as session:
                # 1. Create Companies
                openai_co = Company(name="OpenAI", website="https://openai.com")
                google_co = Company(name="Google", website="https://google.com")
                session.add_all([openai_co, google_co])
                session.flush()

                # 2. Create Providers
                direct_openai = Provider(
                    name="OpenAI", website="https://api.openai.com"
                )
                google_api = Provider(
                    name="Google API",
                    website="https://generativelanguage.googleapis.com",
                )
                session.add_all([direct_openai, google_api])
                session.flush()

                # 3. Create Models
                gpt4 = Model(
                    name="GPT-4o", slug="openai/gpt-4o", company_id=openai_co.id
                )
                gemini = Model(
                    name="Gemini 1.5 Pro",
                    slug="google/gemini-1.5-pro",
                    company_id=google_co.id,
                )
                session.add_all([gpt4, gemini])
                session.flush()

                # 4. Create Mappings (Costs)
                # Cost is in "units" (e.g. 1 unit = 0.00001 cents, adjust as needed)
                m1 = ModelProviderMapping(
                    model_id=gpt4.id,
                    provider_id=direct_openai.id,
                    input_token_cost=5,
                    output_token_cost=15,
                )
                m2 = ModelProviderMapping(
                    model_id=gemini.id,
                    provider_id=google_api.id,
                    input_token_cost=1,
                    output_token_cost=3,
                )
                session.add_all([m1, m2])
                session.commit()

        await conn.run_sync(sync_seed)


if __name__ == "__main__":
    asyncio.run(seed_data())
