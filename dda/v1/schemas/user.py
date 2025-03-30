from datetime import datetime
from ninja import Field
from dda.v1.models.user import UserId
from dda.v1.schemas.base import BaseSchema


_PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"
_EMAIL_REGEX = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
_URL_REGEX = r"^https://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+(?:\.(?:jpe?g|png))?$"


class UserDto(BaseSchema):
    """
    Schema that represents a model of a user that would be
    returned back to the client, including the ID and all information
    that is safe to expose externally, assuming the caller is authorized.
    """
    email: str
    family_name: str
    given_name: str
    id: UserId
    phone_number: str | None = None
    profile_picture: str | None = None


class UserCreateDto(BaseSchema):
    """
    Schema that represents the information (and validations) needed
    to create a new user.
    """
    email: str = Field(pattern=_EMAIL_REGEX)
    family_name: str = Field(min_length=1)
    given_name: str = Field(min_length=1)
    is_email_verified: bool = False
    phone_number: str | None = Field(default=None, pattern=_PHONE_REGEX)
    profile_picture: str | None = Field(default=None, pattern=_URL_REGEX)


class UserSessionDto(BaseSchema):
    """
    Schema representing a user session object that should
    be returned back to a caller when a user has been newly
    authenticated or session refreshed.
    """
    token: str
    expires_at: datetime
    user: UserDto
