from dda.v1.models.user import SessionToken
from dda.v1.models.user import User
from dda.v1.models.user import UserSource
from dda.v1.schemas.user import UserCreateDto


class UserService:
    """
    A service containing several functions that allow us
    to easily interact with users within the database.
    """

    @staticmethod
    async def get_user_by_email(email: str) -> User | None:
        """
        Get a user by their email, which should be guaranteed to be
        unique.

        Args:
            email (str): Email used to query for users.

        Returns:
            The user that matches that email, or None if no such user exists.
        """
        return await User.objects.filter(email=email).afirst()

    @staticmethod
    async def get_or_create_user(
        user_create_dto: UserCreateDto, source: UserSource
    ) -> User:
        """
        Create a new user, or returns an existing one.

        Args:
            user_create_dto (UserCreateDto): The creation DTO to feed into the user create.
            source (UserSource): The OAuth source from with this user came.

        Return:
            The new user that was created, or the existing user if it already existed.
        """
        existing_user = await UserService.get_user_by_email(user_create_dto.email)
        if existing_user is not None:
            return existing_user

        return await User.objects.acreate(
            email=user_create_dto.email,
            family_name=user_create_dto.family_name,
            given_name=user_create_dto.given_name,
            is_email_verified=user_create_dto.is_email_verified,
            profile_picture=user_create_dto.profile_picture,
            source=source,
        )

    @staticmethod
    async def refresh_session_token(user: User) -> SessionToken:
        """
        Refreshes a user's session by doing the simplest thing possible:
        removing the current token and creating a new one.

        Args:
            user (User): The user to which we refresh the session.

        Returns:
            The new SessionToken.
        """
        user_session = await user.get_session()
        if user_session is not None:
            await user_session.adelete()
        return await SessionToken.objects.acreate(user=user)

    @staticmethod
    async def get_current_session_user(token: str) -> SessionToken | None:
        """
        Get the session object tied to the current token, if there is any.

        Args:
            token (str): Token found in the Authorization header.

        Returns:
            The current SessionToken object, or None if no session exists
            or the active session has expired.
        """
        current_session = await SessionToken.objects.filter(token=token).afirst()
        if current_session is not None and current_session.is_expired:
            await current_session.adelete()
            return None
        return current_session
