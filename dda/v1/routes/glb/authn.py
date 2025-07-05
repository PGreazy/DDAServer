import logging
from http import HTTPStatus

from ninja import Router
from dda.v1.exceptions import UnauthenticatedError
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest
from dda.v1.routes.http import EmptyAPIResponse
from dda.v1.schemas.authn import GoogleTokenExchangeDto
from dda.v1.schemas.user import UserDto
from dda.v1.schemas.user import UserSessionDto
from dda.v1.services.authn import AuthNService
from dda.v1.services.user import UserService

logger = logging.getLogger("dda")


authn_router = Router(tags=["auth"])


TOKEN_VALIDATION_FAILED_ERROR_CODE = "TokenValidationFailed"


@authn_router.post(
    by_alias=True,
    path="/google",
    response={201: APIResponse[UserSessionDto]},
    summary="From a Google OAuth ID Token, create or refresh a user session.",
)
async def login_with_google(
    request: APIRequest, code_input: GoogleTokenExchangeDto
) -> tuple[int, APIResponse[UserSessionDto]]:
    session_token = await AuthNService.login_with_google(code_input)
    logger.info(
        f"Created session for userId=${session_token.user.id}",
        extra=request.state.dict(),
    )
    return HTTPStatus.CREATED, APIResponse(data=UserSessionDto.from_orm(session_token))


@authn_router.get(
    by_alias=True,
    path="/me",
    response=APIResponse[UserDto],
    summary="Get the currently authenticated user.",
)
async def get_currently_authenticated_user(request: APIRequest) -> APIResponse[UserDto]:
    if request.state.user is None:
        raise UnauthenticatedError()
    logger.info(
        "User requested /me, their profile is being returned.",
        extra=request.state.dict(),
    )
    return APIResponse(data=UserDto.from_orm(request.state.user))


@authn_router.delete(
    by_alias=True,
    path="/logout",
    response={202: EmptyAPIResponse},
    summary="Deactivate the currently active user session.",
)
async def delete_session(request: APIRequest) -> tuple[int, EmptyAPIResponse]:
    if request.state.user is None:
        raise UnauthenticatedError()

    deleted_session = await UserService.destroy_current_session(request.state.user)
    if deleted_session is None:
        # This shouldn't happen, considering if we've made it here we've authenticated
        # against a valid session.
        logger.warning("Call indicated to remove a session that does not exist.")
    else:
        logger.info("User session has been removed.")
    return HTTPStatus.ACCEPTED, EmptyAPIResponse()
