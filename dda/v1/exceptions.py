from abc import ABC
from abc import abstractmethod
from http import HTTPStatus


_UNAUTHORIZED_ERROR_CODE = "UserUnauthorized"
_NOT_FOUND_ERROR_CODE = "ResourceNotFound"
_CONFLICT_ERROR_CODE = "ResourceHasConflict"


class ResourceException(Exception, ABC):
    """
    An abstract class that represents an exception
    that takes in a resource name and ID to return to the
    caller a meaningful message on what happened to the resource.
    """

    resource_name: str
    resource_id: str
    error_code: str = "ResourceException"
    http_status: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, resource_name: str, resource_id: str):
        self.resource_name = resource_name
        self.resource_id = resource_id

    @abstractmethod
    def __str__(self) -> str: ...


class UnauthenticatedError(Exception):
    """
    Wrapper exception to be thrown when a user is unauthenticated,
    meaning either no Authorization header was passed, or the token
    was found to be valid or expired.
    """


class UnauthorizedError(ResourceException):
    """
    Wrapper exception to be thrown when a user attempts
    to perform an action that they are not authorized to perform,
    often resulting in a 403 status code.
    """

    error_code = _UNAUTHORIZED_ERROR_CODE
    http_status = HTTPStatus.FORBIDDEN

    def __str__(self) -> str:
        return f'User was not authorized to access resource "{self.resource_name}" identified by "{self.resource_id}"'


class NotFoundError(ResourceException):
    """
    Wrapper exception for denoting that a resource was not found. Why use this instead of
    the Django built in? So we can customize the error message much easier.
    """

    error_code = _NOT_FOUND_ERROR_CODE
    http_status = HTTPStatus.NOT_FOUND

    def __str__(self) -> str:
        return f'Resource "{self.resource_name}" identified by "{self.resource_id}" was not found'


class ConflictError(ResourceException):
    """
    Wrapper exception denoting when a user tries to act on a resource that
    would conflict with another resource.
    """

    error_code = _CONFLICT_ERROR_CODE
    http_status = HTTPStatus.CONFLICT

    def __str__(self) -> str:
        return f'Operation on resource "{self.resource_name}" identified by "{self.resource_id}" would result in a conflict.'
