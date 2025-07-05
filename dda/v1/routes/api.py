from functools import partial
from django.urls import path
from ninja import NinjaAPI
from ninja.errors import ValidationError
from dda.env import Env
from dda.v1.exceptions import NotFoundError
from dda.v1.exceptions import UnauthenticatedError
from dda.v1.exceptions import UnauthorizedError
from dda.v1.routes.glb import glb_router
from dda.v1.routes.user import user_router
from dda.v1.routes.exception_handlers import handle_general_exceptions
from dda.v1.routes.exception_handlers import handle_google_code_exchange_errors
from dda.v1.routes.exception_handlers import handle_google_token_validation_errors
from dda.v1.routes.exception_handlers import handle_resource_error
from dda.v1.routes.exception_handlers import handle_validation_errors
from dda.v1.routes.exception_handlers import handle_unauthenticated_error
from dda.v1.services.authn.google import ExternalGoogleService

IS_PRODUCTION = Env.get_env() == Env.PRODUCTION


dda_api = NinjaAPI(
    docs_url=None if IS_PRODUCTION else "/docs",  # Disable docs in production
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    title="DDA-API",
)
dda_api.add_router("glb", glb_router)
dda_api.add_router("user", user_router)


# Exception handlers
dda_api.add_exception_handler(
    Exception, partial(handle_general_exceptions, api=dda_api)
)
dda_api.add_exception_handler(
    ExternalGoogleService.TokenValidationException,
    partial(handle_google_token_validation_errors, api=dda_api),
)
dda_api.add_exception_handler(
    ExternalGoogleService.TokenExchangeException,
    partial(handle_google_code_exchange_errors, api=dda_api),
)
dda_api.add_exception_handler(
    ValidationError, partial(handle_validation_errors, api=dda_api)
)
dda_api.add_exception_handler(
    UnauthenticatedError, partial(handle_unauthenticated_error, api=dda_api)
)
dda_api.add_exception_handler(
    UnauthorizedError, partial(handle_resource_error, api=dda_api)
)
dda_api.add_exception_handler(
    NotFoundError, partial(handle_resource_error, api=dda_api)
)


urlpatterns = [path("", dda_api.urls)]
