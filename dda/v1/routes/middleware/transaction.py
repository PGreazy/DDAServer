import logging
import time
import uuid
from typing import Callable
from django.http import HttpRequest
from django.http import HttpResponse
from dda.v1.routes.http import APIRequestState


logger = logging.getLogger("dda")


def transaction_middleware(get_response: Callable[[HttpRequest], HttpResponse]):
    """Middleware to initialize a transaction and time a request."""
    def middleware(request: HttpRequest) -> HttpResponse:
        request.state = APIRequestState(tid=uuid.uuid4())
        logger.info("REQUEST START", extra=request.state.dict())

        start_time = time.time()
        response = get_response(request)
        end_time = time.time()

        total_time_ms = round((end_time - start_time) * 1000)
        logger.info(f"REQUEST END", extra=request.state.dict())
        logger.info(f"Total request time {total_time_ms}ms", extra=request.state.dict())
        return response
    return middleware
