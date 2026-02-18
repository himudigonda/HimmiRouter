import hashlib

from database.models import ApiKey, User
from database.session import get_session
from fastapi import Depends, FastAPI, HTTPException
from shared.security import generate_api_key
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

app = FastAPI(title="OpenRouter Control Plane")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/auth/register")
async def register(
    email: str, password: str, session: AsyncSession = Depends(get_session)
):
    # Simple check if user exists
    existing = await session.exec(select(User).where(User.email == email))
    if existing.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # In production, use passlib/argon2 to hash passwords
    # For now, we simple hash for the sake of the port
    new_user = User(
        email=email,
        hashed_password=hashlib.sha256(password.encode()).hexdigest(),
        credits=1000,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "credits": new_user.credits}


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
