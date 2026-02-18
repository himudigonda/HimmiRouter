import hashlib
import json

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
async def test_streaming_e2e(gateway_ac: AsyncClient):
    # 1. Setup
    email = "stream_tester@example.com"
    raw_key = "sk-or-v1-streamkey"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Cleanup
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        old_user = res.scalar_one_or_none()
        if old_user:
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
            name="StreamKey",
            key_hash=key_hash,
            key_prefix="sk-or-v1-stream",
        )
        session.add(api_key)
        await session.commit()

        user_id = user.id
        initial_credits = user.credits

    # 2. Execution with Mocks
    from unittest.mock import AsyncMock, patch

    # Mock chunks
    class MockChunk:
        def __init__(self, content, usage=None):
            self.content = content
            self.usage = usage

        def model_dump(self):
            return {
                "choices": [{"delta": {"content": self.content}}],
                "usage": self.usage,
            }

    async def mock_stream():
        yield MockChunk("Hello ")
        yield MockChunk("world!")
        # Last chunk with usage
        yield MockChunk("", usage={"prompt_tokens": 10, "completion_tokens": 20})

    with patch("litellm.acompletion", return_value=mock_stream()):
        async with gateway_ac.stream(
            "POST",
            "/v1/chat/completions",
            headers={"Authorization": f"Bearer {raw_key}"},
            json={
                "model": "openai/gpt-4o",
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": True,
            },
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")

            lines = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    lines.append(line)

            assert len(lines) > 0
            assert "[DONE]" in lines[-1]

    # 3. Verification of Billing
    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = select(User).where(User.id == user_id)
        res = await session.execute(stmt)
        updated_user = res.scalar_one()

        # total_cost = (10*5 + 20*15) // 10 = 35
        expected_deduction = 35
        assert updated_user.credits == initial_credits - expected_deduction


@pytest.mark.asyncio
async def test_partial_streaming_billing(gateway_ac: AsyncClient):
    """Verifies that credits are deducted even if the stream is interrupted."""
    email = "interrupted_tester@example.com"
    raw_key = "sk-or-v1-interrupt"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Cleanup
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        old_user = res.scalar_one_or_none()
        if old_user:
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
            name="InterruptKey",
            key_hash=key_hash,
            key_prefix="sk-or-v1-interrupt",
        )
        session.add(api_key)
        await session.commit()
        user_id = user.id
        initial_credits = user.credits

    from unittest.mock import patch

    class MockChunk:
        def __init__(self, content, usage=None):
            self.content = content
            self.usage = usage

        def model_dump(self):
            return {
                "choices": [{"delta": {"content": self.content}}],
                "usage": self.usage,
            }

    async def mock_interrupted_stream():
        yield MockChunk("Partial content...")
        # Simulating usage update BEFORE the stream ends/errors
        yield MockChunk("", usage={"prompt_tokens": 5, "completion_tokens": 5})
        # Simulate interruption
        raise Exception("Connection Lost")

    with patch("litellm.acompletion", return_value=mock_interrupted_stream()):
        try:
            async with gateway_ac.stream(
                "POST",
                "/v1/chat/completions",
                headers={"Authorization": f"Bearer {raw_key}"},
                json={
                    "model": "openai/gpt-4o",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "stream": True,
                },
            ) as response:
                assert response.status_code == 200
                async for line in response.aiter_lines():
                    # Stop after first line to simulate client disconnect
                    break
        except Exception:
            pass

    # Verification: Wait a bit for the generator's `finally` block to execute
    import asyncio

    await asyncio.sleep(0.5)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        stmt = select(User).where(User.id == user_id)
        res = await session.execute(stmt)
        updated_user = res.scalar_one()

        # total_cost = (5*5 + 5*15) // 10 = 10
        assert updated_user.credits == initial_credits - 10
