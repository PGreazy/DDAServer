from django.urls import path
from ninja import NinjaAPI
from dda.env import Env
from dda.v1.routes.glb import glb_router


IS_PRODUCTION = Env.get_env() == Env.PRODUCTION


dda_api = NinjaAPI(
    csrf=True,
    docs_url=None if IS_PRODUCTION else "/docs",  # Disable docs in production
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    title="DDA-API"
)
dda_api.add_router("glb", glb_router)


urlpatterns = [
    path("", dda_api.urls)
]
