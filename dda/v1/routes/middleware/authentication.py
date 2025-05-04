import logging
from asgiref.sync import sync_to_async
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.decorators import sync_and_async_middleware
from dda.v1.routes.http import APIRequest
from dda.v1.routes.middleware.types import ResponseProcessor
from dda.v1.services.user import UserService


logger = logging.getLogger("dda")


@sync_and_async_middleware
def authentication_middleware(
    get_response: ResponseProcessor[HttpRequest],
) -> ResponseProcessor[APIRequest]:
    """Middleware to intercept authentication information and inform the request if none can be found"""

    async def middleware(request: APIRequest) -> HttpResponse:
        authorization_header = request.headers.get("Authorization", "")
        bearer_values = authorization_header.split()
        if len(bearer_values) == 2 and bearer_values[0] == "Bearer":
            token = bearer_values[-1]
            session = await UserService.get_current_session_user(token)
            if session is not None:
                request.state.user = await sync_to_async(lambda: session.user)()
            else:
                logger.warning(
                    "No valid session was found for token, treating request as unauthenticated.",
                    extra=request.state.dict(),
                )
        else:
            logger.warning(
                "Authorization header was invalid or mis-formatted. treating request as unauthenticated.",
                extra=request.state.dict(),
            )
        return await get_response(request)

    return middleware
