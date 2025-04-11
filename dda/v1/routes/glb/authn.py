import logging
from http import HTTPStatus
from ninja import Router
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest
from dda.v1.schemas.authn import GoogleTokenExchangeDto
from dda.v1.schemas.user import UserSessionDto
from dda.v1.services.authn import AuthNService


logger = logging.getLogger("dda")


authn_router = Router(tags=["auth"])


TOKEN_VALIDATION_FAILED_ERROR_CODE = "TokenValidationFailed"


@authn_router.post(
    by_alias=True,
    path="/google",
    response={
        201: APIResponse[UserSessionDto]
    },
    summary="From a Google OAuth ID Token, create or refresh a user session."
)
async def login_with_google(
    request: APIRequest,
    code_input: GoogleTokenExchangeDto
) -> tuple[int, APIResponse[UserSessionDto]]:
    session_token = await AuthNService.login_with_google(code_input)
    logger.info(f"Created session for userId=${session_token.user.id}", extra=request.state.dict())
    return HTTPStatus.CREATED, APIResponse(
        data=UserSessionDto.from_orm(session_token)
    )
