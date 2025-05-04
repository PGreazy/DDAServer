import pytest
from datetime import timedelta
from http import HTTPStatus
from dda.v1.models.user import SessionToken
from dda.v1.schemas.user import UserSessionDto
from tests.types import APICaller
from tests.wrapper import authed_request


async def _delete_user_session(session: UserSessionDto) -> None:
    token = await SessionToken.objects.aget(token=session.token)
    await token.adelete()


async def _expire_user_session(session: UserSessionDto) -> None:
    token = await SessionToken.objects.aget(token=session.token)
    token.expires_at = token.expires_at - timedelta(minutes=30)
    await token.asave()


@pytest.mark.asyncio
async def test_get_authed_user_returns_401_if_no_header_is_supplied(
    api_get: APICaller,
) -> None:
    await api_get("/v1/glb/auth/me", expected_status_code=HTTPStatus.UNAUTHORIZED)


@pytest.mark.parametrize("test_authz_header", ["", "test-token", "Bwerf test-token"])
async def test_get_authed_user_returns_401_if_authorization_header_is_malformed(
    api_get: APICaller, test_authz_header: str
) -> None:
    await api_get(
        "/v1/glb/auth/me",
        expected_status_code=HTTPStatus.UNAUTHORIZED,
        headers={"Authorization": test_authz_header},
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_authed_user_returns_401_if_no_user_session(
    api_get: APICaller,
) -> None:
    authed_api_get = await authed_request(api_get)
    await _delete_user_session(authed_api_get.session)
    await authed_api_get.caller(
        "/v1/glb/auth/me", expected_status_code=HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_authed_user_returns_401_if_user_session_is_expired(
    api_get: APICaller,
) -> None:
    authed_api_get = await authed_request(api_get)
    await _expire_user_session(authed_api_get.session)
    await authed_api_get.caller(
        "/v1/glb/auth/me", expected_status_code=HTTPStatus.UNAUTHORIZED
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_authed_user_returns_200_with_correct_user_if_authenticated(
    api_get: APICaller,
) -> None:
    authed_api_get = await authed_request(api_get)
    response = await authed_api_get.caller("/v1/glb/auth/me")

    assert response.response["email"] == authed_api_get.session.user.email
    assert response.response["familyName"] == authed_api_get.session.user.family_name
    assert response.response["givenName"] == authed_api_get.session.user.given_name
    assert response.response["id"] == str(authed_api_get.session.user.id)
    assert response.response["phoneNumber"] == authed_api_get.session.user.phone_number
    assert (
        response.response["profilePicture"]
        == authed_api_get.session.user.profile_picture
    )
