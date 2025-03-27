from dda.v1.schemas.base import BaseSchema


class GoogleIdTokenDto(BaseSchema):
    """
    An input schema taking only a Google OAuth ID token, that should
    be validated and decrypted in order to create a user.

    Attributes:
        id_token (str): JWT containing Google user profile data.
    """
    id_token: str
