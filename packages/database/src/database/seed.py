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
                groq_co = get_or_create(
                    Company, name="Groq", website="https://groq.com"
                )
                perplexity_co = get_or_create(
                    Company, name="Perplexity", website="https://perplexity.ai"
                )
                mistral_co = get_or_create(
                    Company, name="Mistral AI", website="https://mistral.ai"
                )

                # 2. Create Providers
                providers = {
                    "openai": get_or_create(
                        Provider, name="OpenAI", website="https://api.openai.com"
                    ),
                    "google": get_or_create(
                        Provider, name="Google AI", website="https://ai.google.dev"
                    ),
                    "anthropic": get_or_create(
                        Provider, name="Anthropic", website="https://api.anthropic.com"
                    ),
                    "groq": get_or_create(
                        Provider, name="Groq", website="https://console.groq.com"
                    ),
                    "perplexity": get_or_create(
                        Provider,
                        name="Perplexity",
                        website="https://docs.perplexity.ai",
                    ),
                    "mistral": get_or_create(
                        Provider, name="Mistral", website="https://console.mistral.ai"
                    ),
                }

                # 3. Create Models
                # (Company, Name, Slug, InputCost, OutputCost, ProviderKey)
                models_to_seed = [
                    # OpenAI
                    (openai_co, "GPT-4o", "gpt-4o", 5, 15, "openai"),
                    (openai_co, "GPT-4o Mini", "gpt-4o-mini", 0.15, 0.6, "openai"),
                    (openai_co, "o1-preview", "o1-preview", 15, 60, "openai"),
                    # Anthropic
                    (
                        anthropic_co,
                        "Claude 3.5 Sonnet",
                        "claude-3-5-sonnet-20240620",
                        3,
                        15,
                        "anthropic",
                    ),
                    (
                        anthropic_co,
                        "Claude 3 Opus",
                        "claude-3-opus-20240229",
                        15,
                        75,
                        "anthropic",
                    ),
                    # Google
                    (
                        google_co,
                        "Gemini 1.5 Pro",
                        "gemini-1.5-pro",
                        3.5,
                        10.5,
                        "google",
                    ),
                    (
                        google_co,
                        "Gemini 1.5 Flash",
                        "gemini-1.5-flash",
                        0.35,
                        1.05,
                        "google",
                    ),
                    # Groq (Ultra-fast Llama)
                    (
                        groq_co,
                        "Llama 3 70B (Groq)",
                        "llama3-70b-8192",
                        0.59,
                        0.79,
                        "groq",
                    ),
                    (
                        groq_co,
                        "Llama 3 8B (Groq)",
                        "llama3-8b-8192",
                        0.05,
                        0.10,
                        "groq",
                    ),
                    (
                        groq_co,
                        "Mixtral 8x7b (Groq)",
                        "mixtral-8x7b-32768",
                        0.27,
                        0.27,
                        "groq",
                    ),
                    # Perplexity (Online)
                    (
                        perplexity_co,
                        "Sonar Large Online",
                        "llama-3-sonar-large-32k-online",
                        1,
                        1,
                        "perplexity",
                    ),
                    (
                        perplexity_co,
                        "Sonar Small Chat",
                        "llama-3-sonar-small-32k-chat",
                        0.2,
                        0.2,
                        "perplexity",
                    ),
                    # Mistral
                    (
                        mistral_co,
                        "Mistral Large 2",
                        "mistral-large-latest",
                        3,
                        9,
                        "mistral",
                    ),
                    (mistral_co, "Codestral", "codestral-latest", 1, 3, "mistral"),
                ]

                for co, name, slug, in_cost, out_cost, prov_key in models_to_seed:
                    # Check if model exists
                    m = session.execute(
                        select(Model).where(Model.slug == slug)
                    ).scalar_one_or_none()
                    if not m:
                        m = Model(name=name, slug=slug, company_id=co.id)
                        session.add(m)
                        session.flush()

                    # Check/Create mapping
                    provider = providers[prov_key]
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
