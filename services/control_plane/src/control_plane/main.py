from database.models import ApiKey, Model, User
from database.session import get_session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.auth_utils import hash_password, verify_password
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


from pydantic import BaseModel


class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
async def login(req: AuthRequest, session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.email == req.email)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"id": user.id, "email": user.email, "credits": user.credits}


@app.post("/auth/register")
async def register(req: AuthRequest, session: AsyncSession = Depends(get_session)):
    # Simple check if user exists
    stmt = select(User).where(User.email == req.email)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        credits=5.0,  # $5.00 free trial
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


from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import selectinload


class CompanyResponse(BaseModel):
    name: str
    website: str


class MappingResponse(BaseModel):
    input_token_cost: float
    output_token_cost: float


class ModelResponse(BaseModel):
    id: int
    name: str
    slug: str
    company: Optional[CompanyResponse] = None
    mappings: List[MappingResponse] = []


@app.get("/models", response_model=List[ModelResponse])
async def list_models(session: AsyncSession = Depends(get_session)):
    stmt = select(Model).options(
        selectinload(Model.company), selectinload(Model.mappings)
    )
    res = await session.execute(stmt)
    return res.scalars().all()


@app.get("/users/{user_id}")
async def get_user_status(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "credits": user.credits}


from database.encryption import encrypt
from database.models import UserProviderKey


class ProviderKeyRequest(BaseModel):
    provider_name: str
    api_key: str


@app.post("/users/{user_id}/provider-keys")
async def add_provider_key(
    user_id: int, req: ProviderKeyRequest, session: AsyncSession = Depends(get_session)
):
    # Check if exists
    stmt = select(UserProviderKey).where(
        UserProviderKey.user_id == user_id,
        UserProviderKey.provider_name == req.provider_name,
    )
    existing = await session.execute(stmt)
    key_entry = existing.scalar_one_or_none()

    if key_entry:
        key_entry.encrypted_key = encrypt(req.api_key)
    else:
        key_entry = UserProviderKey(
            user_id=user_id,
            provider_name=req.provider_name,
            encrypted_key=encrypt(req.api_key),
        )
        session.add(key_entry)

    await session.commit()
    return {"status": "success", "provider": req.provider_name}


@app.get("/users/{user_id}/provider-keys")
async def list_provider_keys(
    user_id: int, session: AsyncSession = Depends(get_session)
):
    stmt = select(UserProviderKey).where(UserProviderKey.user_id == user_id)
    res = await session.execute(stmt)
    keys = res.scalars().all()
    return [{"provider": k.provider_name, "configured": True} for k in keys]


@app.delete("/users/{user_id}/provider-keys/{provider_name}")
async def delete_provider_key(
    user_id: int, provider_name: str, session: AsyncSession = Depends(get_session)
):
    stmt = select(UserProviderKey).where(
        UserProviderKey.user_id == user_id,
        UserProviderKey.provider_name == provider_name,
    )
    res = await session.execute(stmt)
    key_entry = res.scalar_one_or_none()

    if key_entry:
        await session.delete(key_entry)
        await session.commit()
        return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Key not found")
