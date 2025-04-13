from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UUIDModel(models.Model):
    """
    Abstract model with an uuid4 id field as a primary key.
    """

    id = models.UUIDField(_("ID"), default=uuid4, primary_key=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Abstract model for adding created and modified fields.
    """

    # We prefer to use the timezone.now instead of an auto_add_now as an original
    # TimeStampedModel uses. It's more convenient approach, coz we could redefine this
    # values easily in the tests.

    created = models.DateTimeField(default=timezone.now, editable=False, blank=True)
    modified = models.DateTimeField(
        editable=False,
        auto_now=True,
    )

    class Meta:
        abstract = True

    def modify(self):
        """
        Dummy method for forcing the instance's modify time.
        """
        self.save()


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Abstract model combined TimeStamped and UUID models.
    """

    class Meta:
        abstract = True
        get_latest_by = "modified"
