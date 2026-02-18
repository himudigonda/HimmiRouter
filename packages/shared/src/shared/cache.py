import os

from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize.text.huggingface import HFTextVectorizer

cache = None

try:
    # Initialize local embedding model via RedisVL vectorizer
    # Using 'all-MiniLM-L6-v2' (384 dims)
    vectorizer = HFTextVectorizer(model="sentence-transformers/all-MiniLM-L6-v2")

    # Initialize Redis Semantic Cache
    cache = SemanticCache(
        name="himmi_cache",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        distance_threshold=0.04,
        vectorizer=vectorizer,
    )
except Exception as e:
    print(
        f"Warning: Failed to initialize Redis Semantic Cache ({e}). Caching disabled."
    )
    cache = None


async def check_cache(prompt: str):
    if not cache:
        return None
    try:
        # acheck performs async vectorization and search
        results = await cache.acheck(prompt=prompt)
        if results:
            return results[0]["response"]
    except Exception as e:
        print(f"Cache check failed: {e}")
    return None


async def store_cache(prompt: str, response: str):
    if not cache:
        return
    try:
        # astore performs async vectorization and storage
        await cache.astore(prompt=prompt, response=response)
    except Exception as e:
        print(f"Cache store failed: {e}")
