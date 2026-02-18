import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(ac: AsyncClient):
    # Use a unique email to avoid integrity conflicts during testing
    import uuid

    email = f"tester_{uuid.uuid4()}@example.com"
    response = await ac.post(
        "/auth/register", params={"email": email, "password": "securepassword123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == email
