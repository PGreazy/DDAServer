from django.db import models


class AbstractDatedModel(models.Model):
    """
    A base model for any models that need to track a lifetime,
    from when it was created, to last updated, to deleted.

    Attributes:
        created_at (datetime): When the model was first created.
        updated_at (datetime): When the model was last updated.
        deleted_at (datetime): When the model was deleted.
    """
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    deleted_at = models.DateField(default=None)

    class Meta:
        abstract = True
