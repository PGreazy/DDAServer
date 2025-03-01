import logging
import time
import uuid
from django.http import HttpRequest
from django.http import HttpResponse
from dda.v1.routes.http import APIRequest
from dda.v1.routes.http import APIRequestState
from dda.v1.routes.middleware.types import ResponseProcessor


logger = logging.getLogger("dda")


def transaction_middleware(get_response: ResponseProcessor[HttpRequest]) -> ResponseProcessor[APIRequest]:
    """Middleware to initialize a transaction and time a request."""
    def middleware(request: APIRequest) -> HttpResponse:
        request.state = APIRequestState(tid=uuid.uuid4())
        logger.info("REQUEST START", extra=request.state.dict())

        start_time = time.time()
        response = get_response(request)
        end_time = time.time()

        total_time_ms = round((end_time - start_time) * 1000)
        logger.info("REQUEST END", extra=request.state.dict())
        logger.info(f"Total request time {total_time_ms}ms", extra=request.state.dict())
        return response
    return middleware
