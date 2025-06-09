from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User
from uuid import UUID

class CustomUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(login=username)
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(user_id=UUID(str(user_id)))
        except (User.DoesNotExist, ValueError):
            return None
