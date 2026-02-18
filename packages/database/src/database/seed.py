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
                # helper to get or create
                def get_or_create(model_class, **kwargs):
                    instance = session.execute(
                        select(model_class).filter_by(**kwargs)
                    ).scalar_one_or_none()
                    if instance:
                        return instance
                    instance = model_class(**kwargs)
                    session.add(instance)
                    session.flush()
                    return instance

                # 1. Create Companies
                openai_co = get_or_create(
                    Company, name="OpenAI", website="https://openai.com"
                )
                google_co = get_or_create(
                    Company, name="Google", website="https://google.com"
                )
                anthropic_co = get_or_create(
                    Company, name="Anthropic", website="https://anthropic.com"
                )

                # 2. Create Providers
                direct_openai = get_or_create(
                    Provider, name="OpenAI", website="https://api.openai.com"
                )
                google_api = get_or_create(
                    Provider,
                    name="Google API",
                    website="https://generativelanguage.googleapis.com",
                )
                anthropic_api = get_or_create(
                    Provider, name="Anthropic", website="https://api.anthropic.com"
                )

                # 3. Create Models
                models_to_seed = [
                    (openai_co, "GPT-5.2 Pro", "openai/gpt-5.2-pro", 50, 150),
                    (openai_co, "o3-mini", "openai/o3-mini", 5, 15),
                    (
                        anthropic_co,
                        "Claude 4.5 Sonnet",
                        "anthropic/claude-4.5-sonnet",
                        30,
                        90,
                    ),
                    (google_co, "Gemini 3.0 Pro", "google/gemini-3.0-pro", 20, 60),
                ]

                for co, name, slug, in_cost, out_cost in models_to_seed:
                    m = session.execute(
                        select(Model).where(Model.slug == slug)
                    ).scalar_one_or_none()
                    if not m:
                        m = Model(name=name, slug=slug, company_id=co.id)
                        session.add(m)
                        session.flush()

                    # Create or update mapping
                    provider = (
                        direct_openai
                        if co == openai_co
                        else (google_api if co == google_co else anthropic_api)
                    )
                    mapping = session.execute(
                        select(ModelProviderMapping).where(
                            ModelProviderMapping.model_id == m.id,
                            ModelProviderMapping.provider_id == provider.id,
                        )
                    ).scalar_one_or_none()

                    if not mapping:
                        mapping = ModelProviderMapping(
                            model_id=m.id,
                            provider_id=provider.id,
                            input_token_cost=in_cost,
                            output_token_cost=out_cost,
                        )
                        session.add(mapping)

                session.commit()

        await conn.run_sync(sync_seed)


if __name__ == "__main__":
    asyncio.run(seed_data())
