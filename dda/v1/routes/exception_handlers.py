import logging
from http import HTTPStatus
from django.http import HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError
from dda.v1.exceptions import UnauthenticatedError
from dda.v1.routes.http import APIRequest
from dda.v1.routes.http import APIResponse
from dda.v1.services.authn.google import ExternalGoogleService

logger = logging.getLogger("dda")


def handle_general_exceptions(
    request: APIRequest,
    exc: Exception,
    api: NinjaAPI
) -> HttpResponse:
    """
    Exception handler for a general exception that should cause a 500, so we
    can sanitize the response.

    Args:
        request (APIRequest): The originating request.
        exc (Exception): The source exception.
        api (NinjaAPI): The root API object serving this request.

    Returns:
        An HttpResponse containing the error information.
    """
    logger.error(
        f"Request failed with outgoing exception: ${str(exc)}",
        extra=request.state.dict()
    )

    return api.create_response(
        request,
        APIResponse(
            error_code="UnknownError",
            error_message="An unknown error has occurred"
        ).model_dump(by_alias=True),
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )

def handle_validation_errors(
    request: APIRequest,
    exc: ValidationError,
    api: NinjaAPI
) -> HttpResponse:
    """
    Exception handler for a validation failure of input coming
    into the API.

    Args:
        request (APIRequest): The originating request.
        exc (Exception): The source exception.
        api (NinjaAPI): The root API object serving this request.

    Returns:
        An HttpResponse containing the error information.
    """
    error_location = ["unknown"]
    if len(exc.errors) > 0:
        # Only handle one at a time, this may not be
        # the best way, we can extend later if need be.
        error = exc.errors[0]
        location = error.get("loc", ["unknown"])
        if location:
            error_location = location

    logger.error(
        f"Request failed with a validation error at location {error_location[-1]}",
        extra=request.state.dict()
    )

    return api.create_response(
        request,
        APIResponse(
            error_code="ValidationError",
            error_message=f"Validation failed at field ${error_location[-1]}"
        ).model_dump(by_alias=True),
        status=HTTPStatus.BAD_REQUEST
    )


def handle_google_token_validation_errors(
    request: APIRequest,
    _exc: ExternalGoogleService.TokenValidationException,
    api: NinjaAPI
) -> HttpResponse:
    """
    Exception handler to catch validation failures for Google ID tokens.

    Args:
        request (APIRequest): The originating request.
        _exc (Exception): The source exception, unused.
        api (NinjaAPI): The root API object serving this request.

    Returns:
        An HttpResponse containing the error information.
    """
    logger.error("Failed to validate Google ID Token, cannot create session.", extra=request.state.dict())
    return api.create_response(
        request,
        APIResponse(
            error_code="InvalidToken",
            error_message="Input token could not be validated"
        ).model_dump(by_alias=True),
        status=HTTPStatus.BAD_REQUEST
    )


def handle_google_code_exchange_errors(
    request: APIRequest,
    _exc: ExternalGoogleService.TokenExchangeException,
    api: NinjaAPI
) -> HttpResponse:
    """
    Exception handler to catch token exchange errors during Google's OAuth flow.

    Args:
        request (APIRequest): The originating request.
        _exc (Exception): The source exception, unused.
        api (NinjaAPI): The root API object serving this request.

    Returns:
        An HttpResponse containing the error information.
    """
    logger.error("Failed to exchange authorization code for ID token, cannot request Google profile.", extra=request.state.dict())
    return api.create_response(
        request,
        APIResponse(
            error_code="TokenExchangeFailed",
            error_message="Could not exchange authorization code for ID token"
        ).model_dump(by_alias=True),
        status=HTTPStatus.BAD_REQUEST
    )


def handle_unauthenticated_error(
    request: APIRequest,
    _exc: UnauthenticatedError,
    api: NinjaAPI
) -> HttpResponse:
    """
    Exception handler to catch authorization finding a user to be unauthenticated
    for an authorized endpoint.

    Args:
        request (APIRequest): The originating request.
        _exc (Exception): The source exception, unused.
        api (NinjaAPI): The root API object serving this request.

    Returns:
        An HttpResponse containing the error information.
    """
    logger.error(f"User requested {request.path} but was unauthenticated", extra=request.state.dict())
    return api.create_response(
        request,
        APIResponse(
            error_code="UserUnauthenticated",
            error_message="Unauthenticated users cannot make this request."
        ).model_dump(by_alias=True),
        status=HTTPStatus.UNAUTHORIZED
    )
