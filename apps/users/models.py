from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from gears.models.jwt import JWTUserModelMixin

from apps.core.abstract.models import BaseModel
from apps.core.helpers import NULLABLE
from apps.users.managers import UserManager


class User(
    JWTUserModelMixin,
    PermissionsMixin,
    AbstractBaseUser,
    BaseModel,
):
    phone_number = models.CharField(
        _("Phone number"),
        max_length=32,
        unique=True,
        **NULLABLE,
    )

    # Standard password field but with ability to leave blank in admin
    password = models.CharField(_("password"), max_length=128, blank=True)

    email = models.EmailField(**NULLABLE)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self) -> str:
        return (
            " ".join([self.first_name, self.last_name]).strip() or f"Noname ({self.id})"
        )

    def get_short_name(self) -> str:
        name = self.first_name or " "
        return " ".join([name[0], self.last_name]).strip() or f"Noname ({self.id})"

    @classmethod
    def normalize_username(cls, username) -> str:
        return str(username)

    def get_public_jwt_data(self) -> dict:
        return {}

    def get_private_jwt_data(self) -> dict:
        return {}
