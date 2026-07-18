from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    AcademyOS platform user.

    Users can belong to one or more organizations through memberships.
    Organization-specific roles will be stored on those memberships.
    """

    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email