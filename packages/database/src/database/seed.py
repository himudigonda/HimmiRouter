import asyncio

from database.models import (
    Company,
    Model,
    ModelProviderMapping,
    Organization,
    Provider,
    User,
)
from database.session import engine
from shared.auth_utils import hash_password
from sqlmodel import select


async def seed_data():
    async with engine.begin() as conn:
        from sqlalchemy.orm import Session as SyncSession

        def sync_seed(connection):
            with SyncSession(bind=connection) as session:

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

                # ── 1. COMPANIES ──────────────────────────────────────────────
                openai_co = get_or_create(
                    Company, name="OpenAI", website="https://openai.com"
                )
                anthropic_co = get_or_create(
                    Company, name="Anthropic", website="https://anthropic.com"
                )
                google_co = get_or_create(
                    Company, name="Google", website="https://google.com"
                )
                meta_co = get_or_create(Company, name="Meta", website="https://meta.ai")
                mistral_co = get_or_create(
                    Company, name="Mistral AI", website="https://mistral.ai"
                )
                deepseek_co = get_or_create(
                    Company, name="DeepSeek", website="https://deepseek.com"
                )
                xai_co = get_or_create(Company, name="xAI", website="https://x.ai")
                perplexity_co = get_or_create(
                    Company, name="Perplexity", website="https://perplexity.ai"
                )
                groq_co = get_or_create(
                    Company, name="Groq", website="https://groq.com"
                )
                alibaba_co = get_or_create(
                    Company, name="Alibaba", website="https://qwen.aliyun.com"
                )
                amazon_co = get_or_create(
                    Company, name="Amazon", website="https://aws.amazon.com"
                )
                cohere_co = get_or_create(
                    Company, name="Cohere", website="https://cohere.com"
                )
                microsoft_co = get_or_create(
                    Company, name="Microsoft", website="https://microsoft.com"
                )
                ollama_co = get_or_create(
                    Company, name="Ollama (Local)", website="https://ollama.com"
                )

                # ── 2. PROVIDERS ──────────────────────────────────────────────
                providers = {
                    "openai": get_or_create(
                        Provider, name="OpenAI", website="https://api.openai.com"
                    ),
                    "anthropic": get_or_create(
                        Provider, name="Anthropic", website="https://api.anthropic.com"
                    ),
                    "google": get_or_create(
                        Provider, name="Google AI", website="https://ai.google.dev"
                    ),
                    "groq": get_or_create(
                        Provider, name="Groq", website="https://console.groq.com"
                    ),
                    "mistral": get_or_create(
                        Provider, name="Mistral", website="https://console.mistral.ai"
                    ),
                    "deepseek": get_or_create(
                        Provider,
                        name="DeepSeek",
                        website="https://platform.deepseek.com",
                    ),
                    "xai": get_or_create(
                        Provider, name="xAI", website="https://x.ai/api"
                    ),
                    "perplexity": get_or_create(
                        Provider,
                        name="Perplexity",
                        website="https://docs.perplexity.ai",
                    ),
                    "bedrock": get_or_create(
                        Provider,
                        name="Amazon Bedrock",
                        website="https://aws.amazon.com/bedrock",
                    ),
                    "ollama": get_or_create(
                        Provider, name="Ollama", website="https://ollama.com"
                    ),
                }

                # ── 3. MODELS ─────────────────────────────────────────────────
                # Format: (company, display_name, slug, context_length, input_cost, output_cost, provider_key)
                # Costs: USD per 1M tokens
                models_to_seed = [
                    # ── OpenAI ────────────────────────────────────────────────
                    (openai_co, "GPT-5.2", "gpt-5.2", 200000, 1.75, 14.00, "openai"),
                    (
                        openai_co,
                        "GPT-5.2 Pro",
                        "gpt-5.2-pro",
                        200000,
                        21.00,
                        168.00,
                        "openai",
                    ),
                    (openai_co, "GPT-5.1", "gpt-5.1", 200000, 1.75, 14.00, "openai"),
                    (
                        openai_co,
                        "GPT-5 Mini",
                        "gpt-5-mini",
                        128000,
                        0.25,
                        2.00,
                        "openai",
                    ),
                    (
                        openai_co,
                        "GPT-5 Nano",
                        "gpt-5-nano",
                        128000,
                        0.05,
                        0.40,
                        "openai",
                    ),
                    (
                        openai_co,
                        "GPT-5.3 Codex",
                        "gpt-5.3-codex",
                        200000,
                        1.75,
                        14.00,
                        "openai",
                    ),
                    (
                        openai_co,
                        "GPT-5.2 Codex",
                        "gpt-5.2-codex",
                        200000,
                        1.75,
                        14.00,
                        "openai",
                    ),
                    (
                        openai_co,
                        "GPT-5.1 Codex",
                        "gpt-5.1-codex",
                        200000,
                        1.75,
                        14.00,
                        "openai",
                    ),
                    (openai_co, "o3", "o3", 200000, 2.00, 8.00, "openai"),
                    (openai_co, "o3 Pro", "o3-pro", 200000, 20.00, 80.00, "openai"),
                    (openai_co, "o3 Mini", "o3-mini", 128000, 1.10, 4.40, "openai"),
                    (openai_co, "o4 Mini", "o4-mini", 128000, 1.10, 4.40, "openai"),
                    (openai_co, "GPT-4.1", "gpt-4.1", 128000, 3.00, 12.00, "openai"),
                    (
                        openai_co,
                        "GPT-4.1 Mini",
                        "gpt-4.1-mini",
                        128000,
                        0.80,
                        3.20,
                        "openai",
                    ),
                    (
                        openai_co,
                        "GPT-4.1 Nano",
                        "gpt-4.1-nano",
                        128000,
                        0.20,
                        0.80,
                        "openai",
                    ),
                    # ── Anthropic (direct) ────────────────────────────────────
                    (
                        anthropic_co,
                        "Claude 4.6 Opus",
                        "claude-4-6-opus",
                        200000,
                        5.00,
                        25.00,
                        "anthropic",
                    ),
                    (
                        anthropic_co,
                        "Claude 4.6 Sonnet",
                        "claude-4-6-sonnet",
                        200000,
                        3.00,
                        15.00,
                        "anthropic",
                    ),
                    (
                        anthropic_co,
                        "Claude Haiku 4.5",
                        "claude-haiku-4.5",
                        200000,
                        0.80,
                        4.00,
                        "anthropic",
                    ),
                    # ── Google ────────────────────────────────────────────────
                    (
                        google_co,
                        "Gemini 3 Pro (Preview)",
                        "gemini-3-pro-preview",
                        2000000,
                        2.00,
                        12.00,
                        "google",
                    ),
                    (
                        google_co,
                        "Gemini 3 Flash (Preview)",
                        "gemini-3-flash-preview",
                        1000000,
                        0.50,
                        3.00,
                        "google",
                    ),
                    (
                        google_co,
                        "Gemini 2.5 Pro",
                        "gemini-2.5-pro",
                        2000000,
                        1.25,
                        10.00,
                        "google",
                    ),
                    (
                        google_co,
                        "Gemini 2.5 Flash",
                        "gemini-2.5-flash",
                        1000000,
                        0.30,
                        2.50,
                        "google",
                    ),
                    (
                        google_co,
                        "Gemini 2.5 Flash-Lite",
                        "gemini-2.5-flash-lite",
                        1000000,
                        0.10,
                        0.40,
                        "google",
                    ),
                    # ── Meta via Groq ────────────────────────────────────────
                    (
                        meta_co,
                        "Llama 4 Maverick",
                        "llama-4-maverick-instruct",
                        128000,
                        0.50,
                        0.77,
                        "groq",
                    ),
                    (
                        meta_co,
                        "Llama 4 Scout",
                        "llama-4-scout-instruct",
                        128000,
                        0.11,
                        0.34,
                        "groq",
                    ),
                    (
                        meta_co,
                        "Llama 3.3 70B",
                        "llama-3.3-70b-versatile",
                        128000,
                        0.59,
                        0.79,
                        "groq",
                    ),
                    (
                        meta_co,
                        "Llama 3.1 8B",
                        "llama-3.1-8b-instant",
                        128000,
                        0.05,
                        0.08,
                        "groq",
                    ),
                    # ── Alibaba Qwen via Groq ─────────────────────────────────
                    (alibaba_co, "Qwen3 32B", "qwen3-32b", 128000, 0.29, 0.59, "groq"),
                    # ── DeepSeek (direct) ─────────────────────────────────────
                    (
                        deepseek_co,
                        "DeepSeek V4",
                        "deepseek-v4",
                        128000,
                        0.27,
                        1.10,
                        "deepseek",
                    ),
                    (
                        deepseek_co,
                        "DeepSeek V3.2",
                        "deepseek-v3.2",
                        128000,
                        0.27,
                        1.10,
                        "deepseek",
                    ),
                    (
                        deepseek_co,
                        "DeepSeek R1",
                        "deepseek-r1",
                        128000,
                        0.55,
                        2.19,
                        "deepseek",
                    ),
                    # ── Mistral AI (direct) ───────────────────────────────────
                    (
                        mistral_co,
                        "Mistral Large 3",
                        "mistral-large-3",
                        128000,
                        0.50,
                        1.50,
                        "mistral",
                    ),
                    (
                        mistral_co,
                        "Mistral Medium 3",
                        "mistral-medium-3",
                        128000,
                        0.40,
                        2.00,
                        "mistral",
                    ),
                    (
                        mistral_co,
                        "Mistral Small 3.2",
                        "mistral-small-3.2",
                        128000,
                        0.10,
                        0.30,
                        "mistral",
                    ),
                    (
                        mistral_co,
                        "Mistral Nemo",
                        "mistral-nemo",
                        128000,
                        0.30,
                        0.30,
                        "mistral",
                    ),
                    (
                        mistral_co,
                        "Codestral 2",
                        "codestral-2",
                        32000,
                        0.30,
                        0.90,
                        "mistral",
                    ),
                    # ── xAI Grok ──────────────────────────────────────────────
                    (xai_co, "Grok 3", "grok-3", 128000, 3.00, 15.00, "xai"),
                    (xai_co, "Grok 3 Mini", "grok-3-mini", 128000, 0.30, 0.50, "xai"),
                    (xai_co, "Grok 4", "grok-4", 128000, 3.00, 15.00, "xai"),
                    (xai_co, "Grok 4.1", "grok-4.1", 128000, 0.20, 0.50, "xai"),
                    (
                        xai_co,
                        "Grok Code Fast 1",
                        "grok-code-fast-1",
                        128000,
                        0.20,
                        1.50,
                        "xai",
                    ),
                    # ── Perplexity ────────────────────────────────────────────
                    (perplexity_co, "Sonar", "sonar", 128000, 1.00, 1.00, "perplexity"),
                    (
                        perplexity_co,
                        "Sonar Pro",
                        "sonar-pro",
                        128000,
                        3.00,
                        15.00,
                        "perplexity",
                    ),
                    (
                        perplexity_co,
                        "Sonar Reasoning",
                        "sonar-reasoning",
                        128000,
                        1.00,
                        5.00,
                        "perplexity",
                    ),
                    (
                        perplexity_co,
                        "Sonar Reasoning Pro",
                        "sonar-reasoning-pro",
                        128000,
                        2.00,
                        8.00,
                        "perplexity",
                    ),
                    (
                        perplexity_co,
                        "Sonar Deep Research",
                        "sonar-deep-research",
                        128000,
                        2.00,
                        8.00,
                        "perplexity",
                    ),
                    # ── Amazon Bedrock ────────────────────────────────────────
                    (
                        amazon_co,
                        "Nova Pro",
                        "amazon.nova-pro-v1:0",
                        300000,
                        0.80,
                        3.20,
                        "bedrock",
                    ),
                    (
                        amazon_co,
                        "Nova Lite",
                        "amazon.nova-lite-v1:0",
                        300000,
                        0.06,
                        0.24,
                        "bedrock",
                    ),
                    (
                        amazon_co,
                        "Nova Micro",
                        "amazon.nova-micro-v1:0",
                        300000,
                        0.035,
                        0.14,
                        "bedrock",
                    ),
                    (
                        anthropic_co,
                        "Claude 4.6 Sonnet (Bedrock)",
                        "anthropic.claude-sonnet-4-6-20260217-v1:0",
                        200000,
                        3.00,
                        15.00,
                        "bedrock",
                    ),
                    (
                        anthropic_co,
                        "Claude 3.7 Sonnet (Bedrock)",
                        "anthropic.claude-3-7-sonnet-20250219-v1:0",
                        200000,
                        3.00,
                        15.00,
                        "bedrock",
                    ),
                    (
                        anthropic_co,
                        "Claude 3.5 Haiku (Bedrock)",
                        "anthropic.claude-3-5-haiku-20241022-v1:0",
                        200000,
                        0.80,
                        4.00,
                        "bedrock",
                    ),
                    (
                        meta_co,
                        "Llama 3.3 70B (Bedrock)",
                        "meta.llama3-3-70b-instruct-v1:0",
                        128000,
                        0.72,
                        0.72,
                        "bedrock",
                    ),
                    (
                        meta_co,
                        "Llama 3.2 90B (Bedrock)",
                        "meta.llama3-2-90b-instruct-v1:0",
                        128000,
                        0.72,
                        0.72,
                        "bedrock",
                    ),
                    (
                        meta_co,
                        "Llama 3.1 70B (Bedrock)",
                        "meta.llama3-1-70b-instruct-v1:0",
                        128000,
                        0.72,
                        0.72,
                        "bedrock",
                    ),
                    (
                        mistral_co,
                        "Mistral Large 3 (Bedrock)",
                        "mistral.mistral-large-3-2512-v1:0",
                        128000,
                        2.00,
                        6.00,
                        "bedrock",
                    ),
                    (
                        deepseek_co,
                        "DeepSeek V3.2 (Bedrock)",
                        "deepseek.deepseek-v3-2-20250514-v1:0",
                        128000,
                        0.62,
                        1.85,
                        "bedrock",
                    ),
                    (
                        cohere_co,
                        "Command R+",
                        "cohere.command-r-plus-v1:0",
                        128000,
                        3.00,
                        15.00,
                        "bedrock",
                    ),
                    (
                        cohere_co,
                        "Command R",
                        "cohere.command-r-v1:0",
                        128000,
                        0.50,
                        1.50,
                        "bedrock",
                    ),
                    # ── Ollama Local ──────────────────────────────────────────
                    (
                        ollama_co,
                        "Llama 4 8B (Local)",
                        "ollama/llama4:8b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Llama 4 Scout (Local)",
                        "ollama/llama4-scout",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Llama 3.3 70B (Local)",
                        "ollama/llama3.3:70b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Llama 3.2 3B (Local)",
                        "ollama/llama3.2:3b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Llama 3.1 8B (Local)",
                        "ollama/llama3.1:8b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "DeepSeek V3.2 (Local)",
                        "ollama/deepseek-v3.2",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "DeepSeek R1 70B (Local)",
                        "ollama/deepseek-r1:70b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "DeepSeek R1 32B (Local)",
                        "ollama/deepseek-r1:32b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "DeepSeek R1 14B (Local)",
                        "ollama/deepseek-r1:14b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "DeepSeek R1 8B (Local)",
                        "ollama/deepseek-r1:8b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 235B A22B (Local)",
                        "ollama/qwen3:235b-a22b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 32B (Local)",
                        "ollama/qwen3:32b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 30B (Local)",
                        "ollama/qwen3:30b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 14B (Local)",
                        "ollama/qwen3:14b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 8B (Local)",
                        "ollama/qwen3:8b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen3 Coder 30B (Local)",
                        "ollama/qwen3-coder:30b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen2.5 72B (Local)",
                        "ollama/qwen2.5:72b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Qwen2.5 Coder 32B (Local)",
                        "ollama/qwen2.5-coder:32b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Mistral Large 3 (Local)",
                        "ollama/mistral-large3",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Mistral Nemo (Local)",
                        "ollama/mistral-nemo",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Gemma 3 27B (Local)",
                        "ollama/gemma3:27b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Gemma 3 12B (Local)",
                        "ollama/gemma3:12b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Gemma 3 4B (Local)",
                        "ollama/gemma3:4b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Phi-4 14B (Local)",
                        "ollama/phi4:14b",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                    (
                        ollama_co,
                        "Phi-4 Mini (Local)",
                        "ollama/phi4-mini",
                        128000,
                        0.00,
                        0.00,
                        "ollama",
                    ),
                ]

                for co, name, slug, ctx, in_cost, out_cost, prov_key in models_to_seed:
                    m = session.execute(
                        select(Model).where(Model.slug == slug)
                    ).scalar_one_or_none()
                    if not m:
                        m = Model(
                            name=name, slug=slug, context_length=ctx, company_id=co.id
                        )
                        session.add(m)
                        session.flush()

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

                # 4. DEFAULT USER + ORG ─────────────────────────────────────
                test_org = get_or_create(Organization, name="Personal", credits=100.0)

                test_user_mail = "test@example.com"
                test_user = session.execute(
                    select(User).where(User.email == test_user_mail)
                ).scalar_one_or_none()

                if not test_user:
                    test_user = User(
                        email=test_user_mail,
                        hashed_password=hash_password("password"),
                        organization_id=test_org.id,
                    )
                    session.add(test_user)

                session.commit()
                print(f"✓ Seeded {len(models_to_seed)} models across all providers.")

        await conn.run_sync(sync_seed)


if __name__ == "__main__":
    asyncio.run(seed_data())
