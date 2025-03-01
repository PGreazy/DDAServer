from django.http import HttpRequest
from ninja import NinjaAPI

dda_api = NinjaAPI(title="DDA-API")


@dda_api.get("/health")
async def get_app_health(request: HttpRequest):
    return {
        "status": "up"
    }
