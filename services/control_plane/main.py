from database.models import ApiKey
from database.session import get_session
from fastapi import Depends, FastAPI
from shared.security import generate_api_key
from sqlmodel.ext.asyncio.session import AsyncSession

app = FastAPI(title="OpenRouter Control Plane")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api-keys/create")
async def create_new_key(
    name: str, user_id: int, session: AsyncSession = Depends(get_session)
):
    raw_key, key_hash = generate_api_key()

    new_key = ApiKey(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        key_prefix=raw_key[:12],  # sk-or-v1-...
    )

    session.add(new_key)
    await session.commit()

    # Return the raw key ONLY once
    return {"id": new_key.id, "name": new_key.name, "api_key": raw_key}
