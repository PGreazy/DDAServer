import logging
from ninja import Router

from dda.v1.routes.http import APIRequest

logger = logging.getLogger("dda")


authn_router = Router(tags=["auth"])


@authn_router.post(
    by_alias=True,
    path="/google",

)
async def login_with_google(request: APIRequest):
    pass
