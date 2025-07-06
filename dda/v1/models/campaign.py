import uuid
from typing import ClassVar
from typing import TypeAlias
from django.db import models
from dda.v1.models.base import AbstractDatedModel


CampaignId: TypeAlias = uuid.UUID


class Campaign(AbstractDatedModel):
    """
    An object representing a campaign that is currently being run
    within DDA.

    Attributes:
        id (UUID): ID of the campaign.
        name (str): User-given name of the campaign
        created_by (User): The user who created the campaign
        description (str): User-given description of the campaign
        icon (str): URL pointing to an icon for the campaign
        status (str): The current status of the campaign.

    """

    class CampaignStatus(models.TextChoices):
        PLANNING = "PLANNING", "PLANNING"
        IN_PROGRESS = "IN_PROGRESS", "IN PROGRESS"
        COMPLETED = "COMPLETED", "COMPLETED"
        ABANDONED = "ABANDONED", "ABANDONED"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(null=False)
    created_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    description = models.CharField(null=False)
    icon = models.CharField()
    status = models.CharField(choices=[s for s in CampaignStatus.choices], null=False)

    objects: ClassVar[models.Manager["Campaign"]]

    @property
    def has_creator_been_deleted(self) -> bool:
        """
        Returns if the creator of the campaign has been deleted (for example,
        someone creates the campaign, quits, requests a full delete, but the campaign
        is still going and the GM role been re-assigned to a different user.
        """
        return self.created_by is None
