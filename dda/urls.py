from django.urls import path

from dda.routes.api import dda_api


urlpatterns = [
    path("", dda_api.urls)
]
