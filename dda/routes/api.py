from django.http import HttpRequest
from ninja import NinjaAPI
from ninja import Schema
from dda.routes.http import APIResponse

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
async def get_app_health(request: HttpRequest):
    """A simple health check to ensure the server is alive"""
    return APIResponse(data=HealthResponse(status="up"))
