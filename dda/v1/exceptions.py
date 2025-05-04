class UnauthenticatedError(Exception):
    """
    Wrapper exception to be thrown when a user is unauthenticated,
    meaning either no Authorization header was passed, or the token
    was found to be valid or expired.
    """
