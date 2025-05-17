from django.db import models

# Create your models here.
import uuid
from django.db import models

class Family(models.Model):
    family_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    family_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.family_name} ({self.family_id})"

    class Meta:
        db_table = 'FAMILIES'


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=256)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=False, blank=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        db_table = 'USERS'