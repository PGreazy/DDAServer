from django.urls import include
from django.urls import path

urlpatterns = [
    path("v1/", include("dda.v1.routes.api"))
]
