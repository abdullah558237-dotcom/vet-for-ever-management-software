from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):  # <-- Name 'User' kar diya
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Clinic Administrator'
        VET = 'VET', 'Veterinarian'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST
    )
    phone_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    @property
    def is_vet(self):
        return self.role == self.Role.VET or self.is_superuser

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST or self.is_superuser
