import logging
from ninja import Router
from ninja import Schema
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest


logger = logging.getLogger("dda")


health_router = Router(tags=["glb", "health"])


class HealthResponse(Schema):
    """
    Response for the /health endpoint

    Attributes:
        status (str): Is the server up?
    """
    status: str


@health_router.get(
    path="/full",
    response=APIResponse[HealthResponse]
)
async def get_app_health(request: APIRequest) -> APIResponse[HealthResponse]:
    """A simple health check to ensure the server is alive"""
    logger.info("Reporting status UP for health check.", extra=request.state.dict())
    return APIResponse(data=HealthResponse(status="up"))
