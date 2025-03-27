import logging
from ninja import Router
from dda.v1.routes.http import APIResponse
from dda.v1.routes.http import APIRequest
from dda.v1.schemas.base import BaseSchema


logger = logging.getLogger("dda")


health_router = Router(tags=["health"])


class HealthDto(BaseSchema):
    """
    Response for the /health endpoint

    Attributes:
        status (str): Is the server up?
    """
    status: str


@health_router.get(
    by_alias=True,
    path="/full",
    response=APIResponse[HealthDto],
    summary="Retrieves an indicator of system health."
)
async def get_app_health(request: APIRequest) -> APIResponse[HealthDto]:
    """A simple health check to ensure the server is alive"""
    logger.info("Reporting status UP for health check.", extra=request.state.dict())
    return APIResponse(data=HealthDto(status="up"))
