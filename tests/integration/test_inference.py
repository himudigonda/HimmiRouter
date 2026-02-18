import hashlib

import pytest
from database.models import ApiKey, User
from database.session import engine
from httpx import ASGITransport, AsyncClient
from inference_gateway.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


@pytest.fixture
async def gateway_ac():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_inference_e2e(gateway_ac: AsyncClient):
    # 1. Setup Phase: Create a User and API Key directly in DB
    email = "inference_tester@example.com"
    raw_key = "sk-or-v1-testkey123"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Cleanup if exists
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        old_user = res.scalar_one_or_none()
        if old_user:
            # Delete associated api keys first due to FK
            key_stmt = select(ApiKey).where(ApiKey.user_id == old_user.id)
            keys = (await session.execute(key_stmt)).scalars().all()
            for k in keys:
                await session.delete(k)
            await session.delete(old_user)
            await session.commit()

        user = User(email=email, hashed_password="hashed", credits=1000)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        api_key = ApiKey(
            user_id=user.id,
            name="TestKey",
            key_hash=key_hash,
            key_prefix="sk-or-v1-test",
        )
        session.add(api_key)
        await session.commit()

        user_id = user.id
        initial_credits = user.credits

    # 2. Execution Phase: Call the Gateway
    from unittest.mock import AsyncMock, patch


    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="Hello world!"))]
    mock_response.usage = AsyncMock(prompt_tokens=10, completion_tokens=20)

    with patch("litellm.acompletion", return_value=mock_response):
        response = await gateway_ac.post(
            "/v1/chat/completions",
            headers={"Authorization": f"Bearer {raw_key}"},
            json={
                "model": "openai/gpt-4o",
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )

    # 3. Verification Phase
    assert response.status_code == 200
    data = response.json()
    assert data["choices"][0]["message"]["content"] == "Hello world!"

    # Check DB for credit deduction
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = select(User).where(User.id == user_id)
        res = await session.execute(stmt)
        updated_user = res.scalar_one()

        # Costs for gpt-4o: input=5, output=15
        # total_cost = (10*5 + 20*15) // 10 = 35
        expected_deduction = 35
        assert updated_user.credits == initial_credits - expected_deduction
