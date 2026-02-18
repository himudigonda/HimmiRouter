from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    credits: float = Field(default=5.0)  # Default $5.00 trial
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
    name: str
    key_hash: str = Field(unique=True, index=True)  # SHA-256
    key_prefix: str  # e.g., "sk-or-v1-..."
    disabled: bool = Field(default=False)
    deleted: bool = Field(default=False)
    credits_consumed: float = Field(default=0.0)
    last_used: Optional[datetime] = None
    user: User = Relationship(back_populates="api_keys")


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    website: str
    models: List["Model"] = Relationship(back_populates="company")


class Model(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(unique=True)
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
