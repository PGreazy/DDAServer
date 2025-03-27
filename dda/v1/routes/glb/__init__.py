from ninja import Router
from dda.v1.routes.glb.authn import authn_router
from dda.v1.routes.glb.health import health_router


glb_router = Router(tags=["glb"])
glb_router.add_router("auth", authn_router)
glb_router.add_router("health", health_router)
