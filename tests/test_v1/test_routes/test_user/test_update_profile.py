import random
import uuid
import pytest
from http import HTTPStatus

from typing_extensions import no_type_check

from dda.v1.models.user import User
from tests.types import APICaller
from tests.wrapper import authed_request


@no_type_check
def _get_test_update_user_body(**kwargs) -> dict[str, str]:
    return {
        "email": f"update_email_{uuid.uuid4()}@email.com",
        "familyName": "Updated Family Name",
        "givenName": "Updated Given Name",
        "phoneNumber": f"+1{''.join(random.choices('123456789', k=10))}",
        "profilePicture": "https://valid-url.com/picture.png",
        **kwargs,
    }


@no_type_check
async def _create_additional_user(**kwargs) -> User:
    return await User.objects.acreate(
        email=f"test_alt_user_{uuid.uuid4()}@email.com",
        family_name="Graham",
        given_name="Austin",
        **kwargs,
    )


@pytest.mark.asyncio
async def test_update_user_profile_returns_400_if_invalid_user_id(
    api_patch: APICaller,
) -> None:
    test_body = _get_test_update_user_body()
    await api_patch(
        "/v1/user/123", body=test_body, expected_status_code=HTTPStatus.BAD_REQUEST
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_401_if_requesting_user_is_not_resource(
    api_patch: APICaller,
) -> None:
    test_body = _get_test_update_user_body()
    authed_api_patch = await authed_request(api_patch)
    await authed_api_patch.caller(
        f"/v1/user/{uuid.uuid4()}",
        body=test_body,
        expected_status_code=HTTPStatus.FORBIDDEN,
    )


@pytest.mark.asyncio
@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_bad_field",
    [
        {"email": ""},
        {"email": "not-an-email"},
        {"familyName": ""},
        {"givenName": ""},
        {"phoneNumber": ""},
        {"phoneNumber": "not-a-phone"},
        {"profilePicture": ""},
        {"profilePicture": "not-a-url"},
    ],
)
async def test_update_user_profile_returns_400_when_field_is_invalid(
    api_patch: APICaller, test_bad_field: dict[str, str | None]
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id

    test_body = _get_test_update_user_body(**test_bad_field)
    await authed_api_patch.caller(
        f"/v1/user/{user_id}",
        body=test_body,
        expected_status_code=HTTPStatus.BAD_REQUEST,
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_409_when_email_is_already_in_use(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    alt_user = await _create_additional_user()
    test_body = _get_test_update_user_body(email=alt_user.email)
    await authed_api_patch.caller(
        f"/v1/user/{user_id}", body=test_body, expected_status_code=HTTPStatus.CONFLICT
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_409_when_phone_is_already_in_use(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    alt_user = await _create_additional_user(
        phone_number=f"+1{''.join(random.choices('123456789', k=10))}"
    )
    test_body = _get_test_update_user_body(phoneNumber=alt_user.phone_number)
    await authed_api_patch.caller(
        f"/v1/user/{user_id}", body=test_body, expected_status_code=HTTPStatus.CONFLICT
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_200_when_updates_can_be_made(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    test_body = _get_test_update_user_body()

    update_response = await authed_api_patch.caller(
        f"/v1/user/{user_id}", body=test_body
    )

    assert update_response.response["email"] == test_body["email"]
    assert update_response.response["familyName"] == test_body["familyName"]
    assert update_response.response["givenName"] == test_body["givenName"]
    assert update_response.response["id"] == str(user_id)
    assert update_response.response["phoneNumber"] == test_body["phoneNumber"]
    assert update_response.response["profilePicture"] == test_body["profilePicture"]

    db_user = await User.objects.aget(id=user_id)
    assert db_user.email == test_body["email"]
    assert db_user.family_name == test_body["familyName"]
    assert db_user.given_name == test_body["givenName"]
    assert db_user.id == user_id
    assert db_user.phone_number == test_body["phoneNumber"]
    assert db_user.profile_picture == test_body["profilePicture"]


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_200_and_doesnt_update_when_not_necessary(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    pre_call_db_user = await User.objects.aget(id=user_id)

    update_response = await authed_api_patch.caller(f"/v1/user/{user_id}", body={})

    assert pre_call_db_user.email == update_response.response["email"]
    assert pre_call_db_user.family_name == update_response.response["familyName"]
    assert pre_call_db_user.given_name == update_response.response["givenName"]
    assert pre_call_db_user.id == user_id
    assert pre_call_db_user.phone_number == update_response.response["phoneNumber"]
    assert (
        pre_call_db_user.profile_picture == update_response.response["profilePicture"]
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_200_and_unverifies_contact_when_changed(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    db_user = await User.objects.aget(id=user_id)
    assert db_user.is_email_verified
    assert db_user.is_phone_verified

    test_body = _get_test_update_user_body()

    await authed_api_patch.caller(f"/v1/user/{user_id}", body=test_body)

    await db_user.arefresh_from_db()

    assert not db_user.is_email_verified
    assert not db_user.is_phone_verified


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_user_profile_returns_200_and_doesnt_unverify_when_contact_not_changed(
    api_patch: APICaller,
) -> None:
    authed_api_patch = await authed_request(api_patch)
    user_id = authed_api_patch.session.user.id
    db_user = await User.objects.aget(id=user_id)
    assert db_user.is_email_verified
    assert db_user.is_phone_verified

    test_body = _get_test_update_user_body()
    del test_body["email"]
    del test_body["phoneNumber"]

    await authed_api_patch.caller(f"/v1/user/{user_id}", body=test_body)

    await db_user.arefresh_from_db()

    assert db_user.is_email_verified
    assert db_user.is_phone_verified
