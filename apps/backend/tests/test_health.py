import pytest
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """
    Test the health check endpoint returns 200 and success status.
    """
    response = await async_client.get("/health")
    assert response.status_code == HTTP_200_OK
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(async_client):
    """
    Test the api v1 health check endpoint returns 200 and success status.
    """
    response = await async_client.get("/api/v1/health")
    assert response.status_code == HTTP_200_OK
    assert response.json()["success"] is True
    assert response.json()["data"]["service"] == "chhoto-backend"
