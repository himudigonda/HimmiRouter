from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    credits: float = Field(default=10.0)  # Shared pool
    created_at: datetime = Field(default_factory=datetime.utcnow)

    users: List["User"] = Relationship(back_populates="organization")
    api_keys: List["ApiKey"] = Relationship(back_populates="organization")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")

    # Deprecated: Credits now live on Organization, but we keep this for migration compatibility if needed?
    # The user snippet REMOVED credits from User. I will remove it to force the migration to move credits to Org.
    # actually, keeping it for now might be safer but the user implies organization has credits.
    # The user snippet shows:
    # class User(...):
    #    ... (no credits field)
    # So I will remove credits from User.

    organization: Optional[Organization] = Relationship(back_populates="users")
    api_keys: List["ApiKey"] = Relationship(back_populates="user")
    provider_keys: List["UserProviderKey"] = Relationship(back_populates="user")


class UserProviderKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    provider_name: str  # e.g. "openai", "google"
    encrypted_key: str  # Encrypted string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="provider_keys")


class ApiKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    organization_id: int = Field(foreign_key="organization.id")  # Key belongs to Org

    name: str
    key_hash: str = Field(unique=True, index=True)  # SHA-256
    key_prefix: str  # e.g., "sk-or-v1-..."
    disabled: bool = Field(default=False)
    deleted: bool = Field(default=False)
    credits_consumed: float = Field(default=0.0)
    last_used: Optional[datetime] = None

    user: User = Relationship(back_populates="api_keys")
    organization: Organization = Relationship(back_populates="api_keys")


class RequestLog(SQLModel, table=True):
    """The Analytics Engine Source."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    organization_id: int = Field(foreign_key="organization.id", index=True)
    api_key_id: int = Field(foreign_key="apikey.id", index=True)
    model_slug: str = Field(index=True)
    provider_name: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    latency_ms: int
    status_code: int = Field(default=200)
    is_cached: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)


class EvaluationPair(SQLModel, table=True):
    """The Data Flywheel: Stores Primary vs Shadow response for RLHF."""

    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str
    primary_model: str
    primary_response: str
    shadow_model: str
    shadow_response: str
    user_preference: Optional[str] = None  # "primary", "shadow", or "tie"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: str
    models: List["Model"] = Relationship(back_populates="company")


class Model(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(unique=True)
    context_length: Optional[int] = Field(default=None)
    company_id: int = Field(foreign_key="company.id")
    company: Company = Relationship(back_populates="models")
    mappings: List["ModelProviderMapping"] = Relationship(back_populates="model")


class Provider(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: str
    mappings: List["ModelProviderMapping"] = Relationship(back_populates="provider")


class ModelProviderMapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: int = Field(foreign_key="model.id")
    provider_id: int = Field(foreign_key="provider.id")
    input_token_cost: float  # USD per 1M
    output_token_cost: float  # USD per 1M
    model: Model = Relationship(back_populates="mappings")
    provider: Provider = Relationship(back_populates="mappings")
