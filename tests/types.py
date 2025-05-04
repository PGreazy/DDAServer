from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import TypeAlias
from ninja import Schema
from dda.v1.schemas.user import UserSessionDto


HeaderDict: TypeAlias = dict[str, str]
QueryParamDict: TypeAlias = dict[str, str]
JSON: TypeAlias = dict[str, Any]


class APIResponse(Schema):
    """
    A small wrapper around an API response, to assist
    in writing meaningful, easy to use and reuse tests.

    Attributes:
        response (JSON): JSON response, if errors present will be an empty dict
        status_code (int): HTTP status code of response
        error_code (str): String error code, if errors are present
    """

    response: JSON
    status_code: int
    error_code: str | None = None


APICaller: TypeAlias = Callable[..., Coroutine[Any, Any, APIResponse]]


@dataclass
class AuthedAPICaller:
    """
    A small wrapper for an authed APICaller such the caller
    has access to both the authenticated user and the caller function
    itself, for convenience.

    Attributes:
        session (UserSessionDto): The newly authenticated user.
        caller (APICaller): APICaller instance to call an API in a test.
    """

    session: UserSessionDto
    caller: APICaller
