from typing import Generic
from typing import TypeVar
from ninja import Field
from ninja import Schema


T = TypeVar("T")


class APIResponse(Schema, Generic[T]):
    """
    A generic response type to be applied anywhere in this application.

    Attributes:
        data (T): The data to be returned on successful operation of the API.
        error_code (str): A machine-understandable error code to be translated by the client.

    Example:
        >>> from ninja import Schema, Router
        >>> from django.http import HttpRequest
        >>> from dda.routes.http import ApiResponse
        >>> router = Router()

        >>> class MyResponse(Schema):
        ...    # Some fields...
        ...    pass

        >>> @router.get(
        ...    path="/some-endpoint"
        ...    response={
        ...        200: ApiResponse[MyResponse]
        ...    }
        ... )
        >>> async def some_endpoint(request: HttpRequest):
        ...    # Some work...
        ...    pass
    """
    data: T
    error_code: str | None = Field(alias="errorCode", default=None)
