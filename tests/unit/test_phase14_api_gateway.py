import pytest
from httpx import AsyncClient, ASGITransport
from services.api_gateway.main import app

@pytest.mark.asyncio
async def test_api_gateway_health_and_correlation_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health", headers={"X-Correlation-ID": "test-trace-999"})
        assert res.status_code == 200
        assert res.headers.get("X-Correlation-ID") == "test-trace-999"
        assert "X-Response-Time-Ms" in res.headers
        data = res.json()
        assert data["status"] == "healthy"
        assert data["routes"] > 10
