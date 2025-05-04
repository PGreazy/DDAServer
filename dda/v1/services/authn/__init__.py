from dda.v1.models.user import UserSource
from dda.v1.models.user import SessionToken
from dda.v1.schemas.authn import GoogleTokenExchangeDto
from dda.v1.services.authn.google import ExternalGoogleService
from dda.v1.services.authn.google import IGoogleService
from dda.v1.services.user import UserService


class AuthNService:
    """
    This services contains a series of static functions that
    take information from OAuth services and turn them into
    new or update users session for DDA.
    """

    @staticmethod
    async def login_with_google(
        token_exchange_dto: GoogleTokenExchangeDto,
        fetch_service: IGoogleService = ExternalGoogleService,
    ) -> SessionToken:
        """
        Performs a session creation with a user incoming from Google with
        a valid Google ID token.

        Args:
            token_exchange_dto (GoogleTokenExchangeDto): A valid Google authorization code.
            fetch_service (IGoogleService): Implementation of service to validate
                                            and decode the Google ID token.

        Returns:
            A refreshed user session, if it can be refreshed.
        """
        # Because the user gets upserted if the token is found to be valid, then
        # we can get away with not using a transaction if for whatever reason the token
        # can't be refreshed. This helps to simplify the django async vs sync craziness.
        id_token = await fetch_service.exchange_auth_token_for_id_token(
            authorization_code=token_exchange_dto.authorization_code,
            code_verifier=token_exchange_dto.code_verifier,
            redirect_uri=token_exchange_dto.redirect_uri,
        )
        user_create_dto = await fetch_service.get_user_profile(id_token)
        user = await UserService.get_or_create_user(
            user_create_dto=user_create_dto, source=UserSource.GOOGLE
        )
        return await UserService.refresh_session_token(user)
