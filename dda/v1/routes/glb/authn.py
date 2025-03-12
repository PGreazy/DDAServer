import logging
from http import HTTPStatus
from django.db import transaction
from ninja import Router
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest
from dda.v1.schemas.authn import GoogleIdTokenDto
from dda.v1.schemas.user import UserSessionDto
from dda.v1.services.authn import AuthNService
from dda.v1.services.authn.google import ExternalGoogleService


logger = logging.getLogger("dda")


authn_router = Router(tags=["auth"])


TOKEN_VALIDATION_FAILED_ERROR_CODE = "TokenValidationFailed"


@authn_router.post(
    by_alias=True,
    path="/google",
    response={
        201: APIResponse[UserSessionDto],
        400: APIResponse[UserSessionDto]
    },
    summary="From a Google OAuth ID Token, create or refresh a user session."
)
async def login_with_google_test(
    request: APIRequest,
    token_input: GoogleIdTokenDto
) -> tuple[int, APIResponse[UserSessionDto]]:
    try:
        session_token = await AuthNService.login_with_google(token_input.id_token)
        logger.info(f"Created session for userId=${session_token.user.id}", extra=request.state.dict())
        return HTTPStatus.CREATED, APIResponse(
            data=UserSessionDto.from_orm(session_token)
        )
    except ExternalGoogleService.TokenValidationException:
        logger.error("Failed to validate Google ID Token, cannot create session.", extra=request.state.dict())
        return HTTPStatus.BAD_REQUEST, APIResponse(
            error_code=TOKEN_VALIDATION_FAILED_ERROR_CODE
        )
