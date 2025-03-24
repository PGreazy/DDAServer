import pytest
from http import HTTPStatus
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


@pytest.mark.asyncio
async def test_google_login_should_return_400_if_attributes_are_missing(api_post: APICaller) -> None:
    session_token_response = await api_post(
        "/v1/glb/auth/google",
        body={},
        expected_status_code=HTTPStatus.BAD_REQUEST
    )
    assert session_token_response.error_code == "ValidationError"


class MockGoogleService(IGoogleService):

    @staticmethod
    async def get_user_profile(gid_token: str) -> UserCreateDto:
        return TEST_OAUTH_RESPONSE_USER


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
async def test_google_login_should_return_201_when_token_is_created(api_post: APICaller) -> None:
    original_login_with_google = AuthNService.login_with_google
    async def login_with_google_with_mock_fetcher(id_token: str) -> SessionToken:
        return await original_login_with_google(id_token, MockGoogleService)

    test_token_body = {
        "idToken": "some-token"
    }

    with patch.object(AuthNService, "login_with_google", new=login_with_google_with_mock_fetcher):
        session_token_response = await api_post(
            "/v1/glb/auth/google",
            body=test_token_body,
            expected_status_code=HTTPStatus.CREATED
        )
        assert session_token_response.response["token"] is not None
        assert len(session_token_response.response["token"]) > 0
