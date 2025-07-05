from typing import cast
from dda.v1.models.user import SessionToken, UserId
from dda.v1.models.user import User
from dda.v1.models.user import UserSource
from dda.v1.schemas.user import UserCreateDto
from dda.v1.schemas.user import UserUpdateDto


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
    async def get_user_by_id(user_id: UserId) -> User | None:
        """
        Get a user by ID.

        Args:
            user_id (UserId): User ID by which to fetch the user.

        Returns:
            The requested user, if it exists.
        """
        return await User.objects.filter(id=user_id).afirst()

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
    async def update_user_profile(user_update_dto: UserUpdateDto, user: User) -> User:
        """
        Update a user's profile. If email or phone is updated, it will trigger the
        verification flow for the contact information.

        Args:
            user_update_dto: DTO object containing user update info.
            user: User object to update.

        Returns:
            The updated user object.
        """
        email_has_changed = (
            user_update_dto.email is not None and user.email != user_update_dto.email
        )
        user.is_email_verified = (
            user.is_email_verified if not email_has_changed else False
        )
        user.email = (
            user.email if user_update_dto.email is None else user_update_dto.email
        )
        user.family_name = (
            user.family_name
            if user_update_dto.family_name is None
            else user_update_dto.family_name
        )
        user.given_name = (
            user.given_name
            if user_update_dto.given_name is None
            else user_update_dto.given_name
        )
        phone_has_changed = (
            user_update_dto.phone_number is not None
            and user.phone_number != user_update_dto.phone_number
        )
        user.is_phone_verified = (
            user.is_phone_verified if not phone_has_changed else False
        )
        user.phone_number = (
            user.phone_number
            if user_update_dto.phone_number is None
            else user_update_dto.phone_number
        )
        user.profile_picture = (
            user.profile_picture
            if user_update_dto.profile_picture is None
            else user_update_dto.profile_picture
        )
        await user.asave()
        return user

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

    @staticmethod
    async def destroy_current_session(user: User) -> SessionToken | None:
        """
        Destroys the user's session, if there is one. If there isn't,
        then fail silently since there's nothing to destroy.

        Args:
            user: The user whose session we should be destroying.

        Returns:
            The removed session, if there was one.
        """
        current_session = cast(SessionToken | None, await user.get_session())
        if current_session is not None:
            await current_session.adelete()
        return current_session
