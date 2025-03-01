import logging
from django.urls import path
from ninja import NinjaAPI
from ninja import Schema
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest


logger = logging.getLogger("dda")

dda_api = NinjaAPI(title="DDA-API")


class HealthResponse(Schema):
    """
    Response for the /health endpoint

    Attributes:
        status (str): Is the server up?
    """
    status: str


@dda_api.get(
    path="/health",
    response={
        200: APIResponse[HealthResponse]
    }
)
async def get_app_health(request: APIRequest) -> APIResponse[HealthResponse]:
    """A simple health check to ensure the server is alive"""
    logger.info("Reporting status UP for health check.", extra=request.state.dict())
    return APIResponse(data=HealthResponse(status="up"))


urlpatterns = [
    path("", dda_api.urls)
]
