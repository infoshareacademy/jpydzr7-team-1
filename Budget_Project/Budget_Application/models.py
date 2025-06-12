from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid
from datetime import timedelta
import random
import string
from django.conf import settings



class DataTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='id_user')
    transaction_date = models.DateField()
    income = models.FloatField(blank=True, null=True)
    expense = models.FloatField(blank=True, null=True)
    description = models.CharField(blank=True, null=True, max_length=255)
    category = models.ForeignKey('Categories', on_delete=models.CASCADE)
    transaction_type = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        db_table = 'DATA_TRANSACTION'



def generate_access_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


class Family(models.Model):
    family_id = models.UUIDField(default= uuid.uuid4, editable=False)
    family_name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_families')
    created_at = models.DateTimeField(auto_now_add=True)  # Data utworzenia

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
    email = models.EmailField(unique=True)
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


def get_expiration_date():
    return timezone.now() + timedelta(days=7)

class FamilyInvitation(models.Model):
    access_code = models.CharField(max_length=6, unique=True)
    email = models.EmailField()
    family = models.ForeignKey('Family', on_delete=models.CASCADE)
    invited_by = models.ForeignKey('User', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_date)

    def is_valid(self):
        return not self.accepted and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.email} | {self.family.family_name} | Kod: {self.access_code}"

    class Meta:
        db_table = 'INVITATIONS'


class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'REQUESTS'

    def __str__(self):
        return f"{self.user} -> {self.family} ({'accepted' if self.accepted else 'pending'})"

class Categories(models.Model):

    ROLE_CHOICES = (
        ('income', 'income'),
        ('expense', 'expense'),
    )
    category_name = models.CharField(default= None, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    category_type = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'CATEGORIES'

    def __str__(self):
        return self.category_name
