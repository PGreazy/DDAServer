import pytest
from http import HTTPStatus
from tests.conftest import APICaller


@pytest.mark.asyncio
async def test_should_return_200_when_app_is_up(api_get: APICaller):
    health_response = await api_get("/v1/glb/health/full", expected_status_code=HTTPStatus.OK)
    assert health_response.response["status"] == "up"
