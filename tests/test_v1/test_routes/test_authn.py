import pytest
from http import HTTPStatus
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import TypeAlias
from unittest.mock import patch
from dda.v1.models.user import SessionToken
from dda.v1.schemas.user import UserCreateDto
from dda.v1.services.authn import AuthNService
from dda.v1.services.authn.google import ExternalGoogleService
from dda.v1.services.authn.google import IGoogleService
from tests.types import APICaller


TEST_OAUTH_RESPONSE_USER = UserCreateDto(
    email="test@email.com",
    family_name="Graham",
    given_name="Austin",
    is_email_verified=True,
    profile_picture="https://fakepic.com/picture.png"
)


TEST_TOKEN_BODY = {
    "idToken": "sometoken"
}


MockedLoginCallable: TypeAlias = Callable[[str], Coroutine[Any, Any, SessionToken]]

class MockGoogleService(IGoogleService):

    @staticmethod
    async def get_user_profile(gid_token: str) -> UserCreateDto:
        return TEST_OAUTH_RESPONSE_USER


@pytest.fixture
def mocked_google_oauth() -> MockedLoginCallable:
    original_login_with_google = AuthNService.login_with_google
    async def login_with_google_with_mock_fetcher(id_token: str) -> SessionToken:
        return await original_login_with_google(id_token, MockGoogleService)
    return login_with_google_with_mock_fetcher


@pytest.mark.asyncio
async def test_google_login_should_return_400_if_attributes_are_missing(api_post: APICaller) -> None:
    session_token_response = await api_post(
        "/v1/glb/auth/google",
        body={},
        expected_status_code=HTTPStatus.BAD_REQUEST
    )
    assert session_token_response.error_code == "ValidationError"


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_google_login_should_return_400_when_token_cannot_be_verified(api_post: APICaller) -> None:
    async def login_with_google_with_exception(id_token: str) -> SessionToken:
        raise ExternalGoogleService.TokenValidationException()

    test_token_body = {
        "idToken": "some-token"
    }

    with patch.object(AuthNService, "login_with_google", new=login_with_google_with_exception):
        session_token_response = await api_post(
            "/v1/glb/auth/google",
            body=test_token_body,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert session_token_response.error_code == "InvalidToken"


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_google_login_should_return_201_when_token_is_created(
    api_post: APICaller,
    mocked_google_oauth: MockedLoginCallable
) -> None:
    with patch.object(AuthNService, "login_with_google", new=mocked_google_oauth):
        session_token_response = await api_post(
            "/v1/glb/auth/google",
            body=TEST_TOKEN_BODY,
            expected_status_code=HTTPStatus.CREATED
        )
        assert session_token_response.response["token"] is not None
        assert len(session_token_response.response["token"]) > 0
        assert session_token_response.response["user"]["email"] == TEST_OAUTH_RESPONSE_USER.email
        assert session_token_response.response["user"]["familyName"] == TEST_OAUTH_RESPONSE_USER.family_name
        assert session_token_response.response["user"]["givenName"] == TEST_OAUTH_RESPONSE_USER.given_name
        assert session_token_response.response["user"]["phoneNumber"] == TEST_OAUTH_RESPONSE_USER.phone_number
        assert session_token_response.response["user"]["profilePicture"] == TEST_OAUTH_RESPONSE_USER.profile_picture


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_google_login_should_return_201_with_replaced_session_when_session_exists(
    api_post: APICaller,
    mocked_google_oauth: MockedLoginCallable
) -> None:
    with patch.object(AuthNService, "login_with_google", new=mocked_google_oauth):
        # Get a fresh session
        session_token_response = await api_post(
            "/v1/glb/auth/google",
            body=TEST_TOKEN_BODY,
            expected_status_code=HTTPStatus.CREATED
        )
        assert session_token_response.response["token"] is not None
        first_token = session_token_response.response["token"]

        # Now try and replace it
        session_token_response = await api_post(
            "/v1/glb/auth/google",
            body=TEST_TOKEN_BODY,
            expected_status_code=HTTPStatus.CREATED
        )
        assert session_token_response.response["token"] is not None
        second_token = session_token_response.response["token"]

        assert first_token != second_token
        assert await SessionToken.objects.filter(token=first_token).afirst() is None
