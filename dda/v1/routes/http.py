import uuid
from typing import Generic
from typing import TypeAlias
from typing import TypeVar
from django.http import HttpRequest
from ninja import Field
from ninja import Schema
from pydantic import computed_field
from pydantic import ConfigDict
from dda.v1.models.user import User
from dda.v1.models.user import UserId
from dda.v1.schemas.base import BaseSchema


T = TypeVar("T")


class APIResponse(BaseSchema, Generic[T]):
    """
    A generic response type to be applied anywhere in this application.

    Attributes:
        data (T): The data to be returned on successful operation of the API.
        error_code (str): A machine-understandable error code to be translated by the client.
        error_message (str): A human-understandable error message a user can take action on.

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

    data: T | None = None
    error_code: str | None = None
    error_message: str | None = None


class EmptyAPIResponse(APIResponse[object]):
    """
    An extension of the generic response object `APIResponse` meant to
    return an empty response with no errors.
    """

    data: object = {}


TransactionId: TypeAlias = uuid.UUID


class APIRequestState(Schema):
    """
    A class that represents additional state to be tagged onto
    a request before the actual handler has completed.

    Attributes:
        tid (TransactionId): A unique UUID for the request.
        user (User): The user currently authenticated, if there is one.
    """

    tid: TransactionId | None = None
    user: User | None = Field(default=None, exclude=True)

    @property
    @computed_field
    def user_id(self) -> UserId | None:
        if self.user is not None:
            return self.user.id
        return None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class APIRequest(HttpRequest):
    """
    APIRequest extends the base django HttpRequest to include
    a state value, which will contain various request state. This
    is used purely for typing reasons, and should not be instantiated.

    Attributes:
        state (APIRequestState): Custom state attached to a request.
    """

    state: APIRequestState
