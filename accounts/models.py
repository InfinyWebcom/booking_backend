from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Role(models.Model):
    ROLE_CHOICES = [("Owner", "owner"), ("User", "user"), ("Admin", "admin")]
    name = models.CharField(
        max_length=256, blank=False, null=False, unique=True, choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    # username = None
    email = models.EmailField("email address", unique=True)
    contact = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True, blank=True, default=True)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    booking_status = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_signup = models.BooleanField(default=False)
    is_signin = models.BooleanField(default=False)
    wallet = models.IntegerField(default=0)
    last_login_time = models.DateTimeField(max_length=100, null=True, blank=True)
    last_logout_time = models.DateTimeField(max_length=100, null=True, blank=True)
    temp_code = models.BigIntegerField(null=True, blank=True)
    temp_timestamp = models.DateTimeField(max_length=100, null=True, blank=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"  # make the user log in with the email
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
