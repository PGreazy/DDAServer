import logging
from abc import ABC
from abc import abstractmethod
from asgiref.sync import sync_to_async
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from dda.v1.schemas.user import UserCreateDto


logger = logging.getLogger("dda")


class IGoogleService(ABC):
    """
    Interface defining behavior for any class that provides
    the ability to interact with Google APIs.
    """

    @staticmethod
    @abstractmethod
    async def get_user_profile(gid_token: str) -> UserCreateDto:
        """
        Validate the given id_token and construct the user creation
        DTO from it, to be passed down into our own system to return
        a user session.

        Args:
            gid_token (str): A Google ID token.

        Returns:
            A UserCreateDto containing data necessary to create or refresh
            a user session within DDA.
        """
        ...


class ExternalGoogleService(IGoogleService):
    """
    Implementer of IGoogleService that uses the real Google APIs
    in order to fetch a user profile from a Google ID Token.
    """

    class TokenValidationException(Exception):
        """
        Wrapper Exception to make it easier to differentiate
        for callers of get_user_profile that the token failed to
        validate vs some other downstream exception.
        """

    @staticmethod
    async def get_user_profile(gid_token: str) -> UserCreateDto:
        try:
            id_info = await sync_to_async(id_token.verify_oauth2_token)(
                audience=settings.GOOGLE_CLIENT_ID,
                id_token=gid_token,
                request=requests.Request()  # type: ignore[no-untyped-call]
            )
            return UserCreateDto(
                email=id_info["email"],
                family_name=id_info["family_name"],
                given_name=id_info["given_name"],
                is_email_verified=id_info["email_verified"],
                profile_picture=id_info.get("picture", None)
            )
        except Exception as e:
            logger.debug(f"Failure to validate Google token: {e}")
            raise ExternalGoogleService.TokenValidationException()
