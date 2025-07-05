import uuid
import pytest
from http import HTTPStatus
from tests.types import APICaller
from tests.wrapper import authed_request


@pytest.mark.asyncio
async def test_get_user_profile_returns_400_if_invalid_user_id(
    api_get: APICaller,
) -> None:
    await api_get("/v1/user/123", expected_status_code=HTTPStatus.BAD_REQUEST)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_user_profile_returns_401_if_requesting_user_is_not_resource(
    api_get: APICaller,
) -> None:
    authed_api_get = await authed_request(api_get)
    await authed_api_get.caller(
        f"/v1/user/{uuid.uuid4()}", expected_status_code=HTTPStatus.FORBIDDEN
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_user_profile_returns_200_with_correct_user(
    api_get: APICaller,
) -> None:
    authed_api_get = await authed_request(api_get)
    response = await authed_api_get.caller(f"/v1/user/{authed_api_get.session.user.id}")

    assert response.response["email"] == authed_api_get.session.user.email
    assert response.response["familyName"] == authed_api_get.session.user.family_name
    assert response.response["givenName"] == authed_api_get.session.user.given_name
    assert response.response["id"] == str(authed_api_get.session.user.id)
    assert response.response["phoneNumber"] == authed_api_get.session.user.phone_number
    assert (
        response.response["profilePicture"]
        == authed_api_get.session.user.profile_picture
    )


@pytest.mark.skip("Skipped until proper team/campaign logic is implemented.")
async def test_get_user_profile_returns_200_if_different_user_but_authorized(
    api_get: APICaller,
) -> None: ...
