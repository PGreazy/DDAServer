from functools import partial
from django.urls import path
from ninja import NinjaAPI
from ninja.errors import ValidationError
from dda.env import Env
from dda.v1.routes.glb import glb_router
from dda.v1.routes.exception_handlers import handle_general_exceptions
from dda.v1.routes.exception_handlers import handle_validation_errors


IS_PRODUCTION = Env.get_env() == Env.PRODUCTION


dda_api = NinjaAPI(
    docs_url=None if IS_PRODUCTION else "/docs",  # Disable docs in production
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    title="DDA-API"
)
dda_api.add_router("glb", glb_router)


# Exception handlers
dda_api.add_exception_handler(Exception, partial(handle_general_exceptions, api=dda_api))
dda_api.add_exception_handler(ValidationError, partial(handle_validation_errors, api=dda_api))


urlpatterns = [
    path("", dda_api.urls)
]
