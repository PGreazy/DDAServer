import uuid
from asgiref.sync import sync_to_async
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
from typing import ClassVar
from typing import no_type_check
from typing import Optional
from typing import TypeAlias
from django.db import models
from django.conf import settings
from dda.v1.models.base import AbstractDatedModel


class UserSource(Enum):
    GOOGLE = "google"


UserId: TypeAlias = uuid.UUID


class User(AbstractDatedModel):
    """
    A user in the DDA system, having been sourced by an OAuth provider.

    Attributes:
        email (str): The user's email.
        family_name (str): The user's surname.
        given_name (str): The user's first name.
        id (UUID): A unique ID assigned by our system. Auto-generated on create.
        is_email_verified (bool): Has the user verified their email?
        phone_number (str): The user's phone number in E.164 format.
        profile_picture (str): A link to the user's profile photo, if present.
        source (str): Where the original user signup came from.
    """
    email = models.CharField(null=False, unique=True)
    family_name = models.CharField(null=False)
    given_name = models.CharField(null=False)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(null=True, unique=True)
    profile_picture = models.CharField(null=True)
    source = models.CharField(
        choices=[(entry.name, entry.value) for entry in UserSource],
        null=False
    )

    objects: ClassVar[models.Manager["User"]]

    @no_type_check
    async def get_session(self) -> Optional["SessionToken"]:
        """
        Custom wrapper around the OneToOneField for a session to allow
        getting a None back if the session does not exist.
        """
        try:
            return await sync_to_async(lambda: self.session)()
        except User.session.RelatedObjectDoesNotExist:
            return None

    def __str__(self) -> str:
        return f"{id}"


def _generate_session_token() -> str:
    return f"tk-{''.join(str(uuid.uuid4()).split('-'))}"


def _get_expiry_date() -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(minutes=settings.SESSION_LENGTH_MINUTES)


class SessionToken(models.Model):
    """
    A token that ties to a user and marks their session. Should be used
    as an authentication method for any API that requires fetching data.

    Attributes:
        token (str): The token identifying the session.
        expires_at (datetime): The time when this token expires.
        user (User): The user associated with this token.
    """
    token = models.CharField(default=_generate_session_token, null=False, primary_key=True)
    expires_at = models.DateTimeField(default=_get_expiry_date, null=False)
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name="session"
    )

    objects: ClassVar[models.Manager["SessionToken"]]

    @property
    def is_expired(self) -> bool:
        """
        Convenience property to compute if this token is expired, based
        on the current UTC time and the marked expiry time on the token.

        Returns:
            True if the current time is greater than the expired time, False otherwise.
        """
        current_time = datetime.now(tz=timezone.utc)
        return current_time >= self.expires_at
