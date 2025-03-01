import uuid
from typing import Generic
from typing import TypeAlias
from typing import TypeVar
from django.http import HttpRequest
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
        >>> from dda.v1.routes.http import ApiResponse
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


TransactionId: TypeAlias = uuid.UUID


class APIRequestState(Schema):
    """
    A class that represents additional state to be tagged onto
    a request before the actual handler has completed.

    Attributes:
        tid (TransactionId): A unique UUID for the request.
        user_id (str): The user ID currently authenticated, if there is one.
    """
    tid: TransactionId
    # Update type when I can
    user_id: str | None = None


class APIRequest(HttpRequest):
    """
    APIRequest extends the base django HttpRequest to include
    a state value, which will contain various request state. This
    is used purely for typing reasons, and should not be instantiated.

    Attributes:
        state (APIRequestState): Custom state attached to a request.
    """
    state: APIRequestState
