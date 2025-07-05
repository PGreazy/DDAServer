from http import HTTPStatus

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
    """Get a Django async test client for use by the entire test suite"""
    return AsyncClient()


async def _fetch_resource(
    request_method_caller: Callable[..., Any],  # No proper type for an ASGI response...
    path: str,
    body: dict[str, Any] | None = None,
    expected_status_code: int = HTTPStatus.OK,
    headers: HeaderDict | None = None,
    query_params: QueryParamDict | None = None,
) -> APIResponse:
    """
    Given a method to execute an HTTP request, make the request, parse
    for the expected status and expected return format based on that status,
    and return back for the caller to further assert.

    Args:
        request_method_caller (Callable): An AsyncClient extension method to execute an HTTP request.
        path (str): A path on which to execute the request.
        expected_status_code (int): The expected status code on which we will assert is present on the response.
        headers (HeaderDict): Any headers to pass with the request.
        query_params (QueryParamDict): Any query params to include in the request

    Returns:
        An await-ed response from the given request configuration in a custom format (APIResponse) to make assertion
        simpler. If the request is successful and data is returned, the inner object form the "data" entry
        will be stripped and returned in APIResponse.
    """
    response = await request_method_caller(
        data=body,
        content_type="application/json",
        headers=headers if headers is not None else {},
        path=path,
        query_params=query_params,
    )
    if expected_status_code is not None:
        assert expected_status_code == response.status_code
    response_json = response.json()
    assert "data" in response_json
    assert "errorCode" in response_json
    if response.status_code >= 400:
        assert response_json["data"] is None
        return APIResponse(
            error_code=response_json["errorCode"],
            response={},
            status_code=response.status_code,
        )
    assert response_json["errorCode"] is None
    return APIResponse(response=response_json["data"], status_code=response.status_code)


@pytest.fixture(scope="session")
def api_get(api_test_client: AsyncClient) -> APICaller:
    """Gets a callable that will GET on a given REST resource."""
    return partial(_fetch_resource, api_test_client.get)


@pytest.fixture(scope="session")
def api_post(api_test_client: AsyncClient) -> APICaller:
    """Gets a callable that will POST on a given REST resource."""
    return partial(_fetch_resource, api_test_client.post)


@pytest.fixture(scope="session")
def api_delete(api_test_client: AsyncClient) -> APICaller:
    """Gets a callable that will DELETE on a given REST resource."""
    return partial(_fetch_resource, api_test_client.delete)


@pytest.fixture(scope="session")
def api_patch(api_test_client: AsyncClient) -> APICaller:
    """Gets a callable that will PATCH on a given REST resource."""
    return partial(_fetch_resource, api_test_client.patch)
