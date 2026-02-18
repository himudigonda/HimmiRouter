
import pytest
from control_plane.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def ac():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
