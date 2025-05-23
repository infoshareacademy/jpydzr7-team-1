from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid


class Family(models.Model):
    family_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    family_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.family_name} ({self.family_id})"

    class Meta:
        db_table = 'FAMILIES'


class CustomUserManager(BaseUserManager):
    def create_user(self, login, email, password=None, **extra_fields):
        if not login:
            raise ValueError("Użytkownik musi mieć login.")
        if not email:
            raise ValueError("Użytkownik musi mieć email.")

        email = self.normalize_email(email)
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser musi mieć is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser musi mieć is_superuser=True.')

        return self.create_user(login, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('adult', 'Adult'),
        ('kid', 'Kid'),
    )
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    login = models.CharField(max_length=100, unique=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10,default='kid', choices=ROLE_CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        db_table = 'USERS'