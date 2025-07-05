import pytest
from http import HTTPStatus
from tests.types import APICaller
from tests.wrapper import authed_request


@pytest.mark.asyncio
async def test_logout_user_returns_401_if_no_header_is_supplied(
    api_delete: APICaller,
) -> None:
    await api_delete(
        "/v1/glb/auth/logout", expected_status_code=HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("test_authz_header", ["", "test-token", "Bwerf test-token"])
async def test_logout_user_returns_401_if_authorization_header_is_malformed(
    api_delete: APICaller, test_authz_header: str
) -> None:
    await api_delete(
        "/v1/glb/auth/logout",
        expected_status_code=HTTPStatus.UNAUTHORIZED,
        headers={"Authorization": test_authz_header},
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_logout_user_returns_202_when_session_is_deleted(
    api_delete: APICaller, api_get: APICaller
) -> None:
    authed_api_delete = await authed_request(api_delete)
    await authed_api_delete.caller(
        "/v1/glb/auth/logout", expected_status_code=HTTPStatus.ACCEPTED
    )
    await api_get(
        "/v1/glb/auth/me",
        headers={"Authorization": f"Bearer {authed_api_delete.session.token}"},
        expected_status_code=HTTPStatus.UNAUTHORIZED,
    )
