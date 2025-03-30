from dda.v1.schemas.base import BaseSchema


class GoogleTokenExchangeDto(BaseSchema):
    """
    An input schema taking the result of a Google authorization code request.

    Attributes:
        authorization_code (str): A valid Google authorization code.
        code_verifier (str): The code verifier used to make the original authorization request.
        redirect_uri (str): The original redirect_uri used in the authorization code request.
    """
    authorization_code: str
    code_verifier: str
    redirect_uri: str
