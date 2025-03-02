from django.urls import path
from ninja import NinjaAPI
from dda.v1.routes.glb import glb_router


dda_api = NinjaAPI(title="DDA-API")
dda_api.add_router("glb", glb_router)


urlpatterns = [
    path("", dda_api.urls)
]
