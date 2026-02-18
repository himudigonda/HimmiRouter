from database.models import ApiKey, Company, Model, User
from database.session import get_session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.auth_utils import hash_password
from shared.instrumentation import instrument_app
from shared.security import generate_api_key
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

app = FastAPI(title="OpenRouter Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrument_app(app, "control-plane")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/auth/register")
async def register(
    email: str, password: str, session: AsyncSession = Depends(get_session)
):
    # Simple check if user exists
    existing = await session.execute(select(User).where(User.email == email))
    if existing.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=email,
        hashed_password=hash_password(password),
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


@app.get("/api-keys")
async def list_api_keys(user_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(ApiKey).where(ApiKey.user_id == user_id)
    res = await session.execute(stmt)
    return res.scalars().all()


@app.get("/models")
async def list_models(session: AsyncSession = Depends(get_session)):
    stmt = select(Model)
    res = await session.execute(stmt)
    return res.scalars().all()


@app.get("/users/{user_id}")
async def get_user_status(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "credits": user.credits}
