import logging
from typing import cast
from typing import Protocol
from asgiref.sync import sync_to_async
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from dda.v1.schemas.user import UserCreateDto


logger = logging.getLogger("dda")


_GOOGLE_TOKEN_EXCHANGE_URL = "https://oauth2.googleapis.com/token"


class IGoogleService(Protocol):
    """
    Interface defining behavior for any class that provides
    the ability to interact with Google APIs.
    """

    @staticmethod
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

    @staticmethod
    async def exchange_auth_token_for_id_token(
        authorization_code: str,
        code_verifier: str,
        redirect_uri: str
    ) -> str:
        """
        Exchange an authorization code provided by the client (assumes the client
        has already requested it) for an id_token, which can later be turned into a user profile.

        Args:
            authorization_code (str): Authorization code provided by Google.
            code_verifier (str): Code verifier used to make the original authorization request.
            redirect_uri (str): The redirect URI used in the original code request

        Returns:
            A Google-provided id_token to be turned into a user profile.
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

    class TokenExchangeException(Exception):
        """
        Wrapper exception for when we fail to call the Google
        OAuth APIs to exchange an authorization token for an
        ID token.
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

    @staticmethod
    async def exchange_auth_token_for_id_token(
        authorization_code: str,
        code_verifier: str,
        redirect_uri: str
    ) -> str:
        token_request_data = {
            "code": authorization_code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        request = requests.Request()  # type: ignore
        response = await sync_to_async(request.session.post)(
            _GOOGLE_TOKEN_EXCHANGE_URL,
            data=token_request_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        if response.status_code >= 300:
            logger.debug(f"Failure to request token exchange, got status code: {response.status_code}")
            raise ExternalGoogleService.TokenExchangeException()

        response_json = response.json()
        return cast(str, response_json["id_token"])
