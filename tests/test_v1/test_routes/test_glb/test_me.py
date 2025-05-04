import pytest
from http import HTTPStatus
from dda.v1.models.user import SessionToken
from dda.v1.schemas.user import UserSessionDto
from tests.types import APICaller
from tests.wrapper import authed_request


async def _expire_user_session(session: UserSessionDto) -> None:
    token = await SessionToken.objects.aget(token=session.token)
    await token.adelete()


@pytest.mark.asyncio
async def test_get_authed_user_returns_401_if_no_header_is_supplied(api_get: APICaller) -> None:
    await api_get(
        "/v1/glb/auth/me",
        expected_status_code=HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.parametrize(
    "test_authz_header",
    [
        "",
        "test-token",
        "Bwerf test-token"
    ]
)
async def test_get_authed_user_returns_401_if_authorization_header_is_malformed(api_get: APICaller, test_authz_header: str) -> None:
    await api_get(
        "/v1/glb/auth/me",
        expected_status_code=HTTPStatus.UNAUTHORIZED,
        headers={
            "Authorization": test_authz_header
        }
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_authed_user_returns_401_if_user_session_has_expired(api_get: APICaller) -> None:
    authed_api_get = await authed_request(api_get)
    await _expire_user_session(authed_api_get.session)
    await authed_api_get.caller(
        "/v1/glb/auth/me",
        expected_status_code=HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.asyncio
async def test_get_authed_user_returns_200_with_correct_user_if_authenticated(api_get: APICaller) -> None:
    pass
