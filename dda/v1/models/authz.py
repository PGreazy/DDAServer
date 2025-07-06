from typing import ClassVar
from typing import TypeAlias
from django.db import models
from dda.v1.models.base import AbstractDatedModel


RoleId: TypeAlias = str


class AppRole(AbstractDatedModel):
    """
    Represents the existent of an app role that a user can
    hold on a given campaign./

    Attributes:
        role_name (str): The name of the role, in a machine understandable form.
        friendly_role_name (str): The name of the role in a human-readable form.
    """

    role_name = models.CharField(primary_key=True)
    friendly_role_name = models.CharField(unique=True)

    objects: ClassVar[models.Manager["AppRole"]]


class AppResourceRole(AbstractDatedModel):
    """
    Maps a user to a given role on a given campaign.

    Attributes:
        id: (int): Auto-increment ID for the sake of making the DB happy.
        role (AppRole): The intended role the user should hold.
        user (User): The user holding the role.
        campaign (Campaign): The campaign on which the user is holding the role.
    """

    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(AppRole, on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE)

    objects: ClassVar[models.Manager["AppResourceRole"]]
