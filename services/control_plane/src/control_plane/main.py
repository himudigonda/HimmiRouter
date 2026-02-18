from typing import List, Optional

from database.encryption import encrypt
from database.models import (
    ApiKey,
    EvaluationPair,
    Model,
    Organization,
    RequestLog,
    User,
    UserProviderKey,
)
from database.session import get_session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.auth_utils import hash_password, verify_password
from shared.instrumentation import instrument_app
from shared.security import generate_api_key
from sqlalchemy.orm import selectinload
from sqlmodel import func, select
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


class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
async def login(req: AuthRequest, session: AsyncSession = Depends(get_session)):
    # Eager load organization for credits
    stmt = (
        select(User)
        .where(User.email == req.email)
        .options(selectinload(User.organization))
    )
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.organization:
        credits = 0.0
    else:
        credits = user.organization.credits

    return {"id": user.id, "email": user.email, "credits": credits}


@app.post("/auth/register")
async def register(req: AuthRequest, session: AsyncSession = Depends(get_session)):
    # Simple check if user exists
    stmt = select(User).where(User.email == req.email)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create Organization first
    org_name = f"{req.email}'s Org"
    new_org = Organization(name=org_name, credits=10.0)  # $10.00 as per new default
    session.add(new_org)
    await session.commit()
    await session.refresh(new_org)

    new_user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        organization_id=new_org.id,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"id": new_user.id, "email": new_user.email, "credits": new_org.credits}


@app.post("/api-keys/create")
async def create_new_key(
    name: str, user_id: int, session: AsyncSession = Depends(get_session)
):
    # Fetch user to get Organization ID
    user_stmt = select(User).where(User.id == user_id)
    user_res = await session.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    raw_key, key_hash = generate_api_key()

    new_key = ApiKey(
        user_id=user_id,
        organization_id=user.organization_id,  # Link to Org
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
    stmt = (
        select(User).where(User.id == user_id).options(selectinload(User.organization))
    )
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credits = user.organization.credits if user.organization else 0.0
    return {"id": user.id, "email": user.email, "credits": credits}


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


# --- ANALYTICS ---


@app.get("/analytics/usage")
async def get_usage_stats(user_id: int, session: AsyncSession = Depends(get_session)):
    """Returns real token usage over the last 7 days for the chart."""
    # Query logs grouped by day
    # Note: RequestLog.timestamp is datetime
    date_trunc_expr = func.date_trunc("day", RequestLog.timestamp)
    stmt = (
        select(
            date_trunc_expr.label("date"),
            func.sum(RequestLog.prompt_tokens + RequestLog.completion_tokens).label(
                "tokens"
            ),
            func.sum(RequestLog.cost).label("cost"),
            func.count(RequestLog.id).label("count"),
        )
        .where(RequestLog.user_id == user_id)
        .group_by(date_trunc_expr)
        .order_by(date_trunc_expr)
    )
    res = await session.execute(stmt)
    rows = res.all()

    return [
        {
            "date": r.date.strftime("%Y-%m-%d") if r.date else None,
            "tokens": r.tokens or 0,
            "cost": r.cost or 0.0,
            "count": r.count or 0,
        }
        for r in rows
    ]


@app.get("/analytics/health")
async def get_provider_health(session: AsyncSession = Depends(get_session)):
    """The 'Weather Map' API."""
    stmt = select(
        RequestLog.provider_name,
        func.avg(RequestLog.latency_ms).label("avg_latency"),
        func.count(RequestLog.id).label("total_reqs"),
    ).group_by(RequestLog.provider_name)
    res = await session.execute(stmt)
    return [
        {
            "provider": r.provider_name,
            "avg_latency": r.avg_latency,
            "total_reqs": r.total_reqs,
        }
        for r in res.all()
    ]


# --- PREFERENCE (RLHF) ---


class PreferenceRequest(BaseModel):
    prompt: str
    primary_model: str
    primary_response: str
    shadow_model: str
    shadow_response: str
    user_preference: str  # "primary" or "shadow"


@app.post("/analytics/preference")
async def save_user_preference(
    req: PreferenceRequest, session: AsyncSession = Depends(get_session)
):
    """Saves the RLHF data for future model training."""
    pair = EvaluationPair(
        prompt=req.prompt,
        primary_model=req.primary_model,
        primary_response=req.primary_response,
        shadow_model=req.shadow_model,
        shadow_response=req.shadow_response,
        user_preference=req.user_preference,
    )
    session.add(pair)
    await session.commit()
    return {"status": "recorded"}
