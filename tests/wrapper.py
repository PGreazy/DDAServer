import uuid
from typing import Any
from typing import Coroutine
from dda.v1.models.user import SessionToken
from dda.v1.models.user import User
from dda.v1.models.user import UserSource
from dda.v1.schemas.user import UserSessionDto
from tests.types import APICaller
from tests.types import APIResponse
from tests.types import AuthedAPICaller
from tests.types import HeaderDict


async def _authenticated_session() -> UserSessionDto:
    new_user = await User.objects.acreate(
        email=f"dda_dev_test_{uuid.uuid4()}@email.com",
        family_name="Test",
        given_name="Dev",
        is_email_verified=True,
        source=UserSource.GOOGLE,
    )
    new_token = await SessionToken.objects.acreate(user=new_user)
    return UserSessionDto.from_orm(new_token)


async def authed_request(caller: APICaller) -> AuthedAPICaller:
    """
    Wraps a pytest fixture returning APICaller in a session, in order to test
    authentication and authentication requests.

    Args:
        caller:

    Returns:

    """
    session = await _authenticated_session()

    def _wrap_authorization_header(
        path: str, headers: HeaderDict | None = None, **kwargs: Any
    ) -> Coroutine[Any, Any, APIResponse]:
        headers = {
            **(headers if headers is not None else {}),
            "Authorization": f"Bearer {session.token}",
        }
        return caller(path, headers=headers, **kwargs)

    return AuthedAPICaller(session=session, caller=_wrap_authorization_header)
