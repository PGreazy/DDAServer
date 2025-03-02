import pytest
from functools import partial
from typing import Any
from typing import Callable
from django.test import AsyncClient
from tests.types import APICaller
from tests.types import APIResponse
from tests.types import HeaderDict
from tests.types import QueryParamDict


@pytest.fixture(scope="session")
def api_test_client() -> AsyncClient:
    return AsyncClient()


async def _fetch_resource(
    request_method_caller: Callable[..., Any],  # No proper type for an ASGI response...
    path: str,
    expected_status_code: int | None = None,
    headers: HeaderDict | None = None,
    query_params: QueryParamDict | None = None
) -> APIResponse:
    response = await request_method_caller(
        headers=headers if headers is not None else {},
        path=path,
        query_params=query_params
    )
    if expected_status_code is not None:
        assert expected_status_code == response.status_code
    response_json = response.json()
    if response.status_code >= 400:
        assert "errorCode" in response_json
        return APIResponse(
            error_code=response_json["errorCode"],
            status_code=response.status_code
        )
    assert "data" in response_json
    return APIResponse(
        response=response_json["data"],
        status_code=response.status_code
    )


@pytest.fixture(scope="session")
def api_get(api_test_client: AsyncClient) -> APICaller:
    return partial(
        _fetch_resource,
        api_test_client.get
    )
