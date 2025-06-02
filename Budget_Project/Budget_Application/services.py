from django.contrib.auth.hashers import check_password
from .models import User

class UserService:
    @staticmethod
    def get_user_by_login(login):
        try:
            return User.objects.get(login=login.strip().lower())
        except User.DoesNotExist:
            return None

    @staticmethod
    def remove_user_by_login_and_password(login, raw_password):
        try:
            user = User.objects.get(login=login.strip().lower())

            if check_password(raw_password, user.password):
                user.delete()
                return True, f"Użytkownik o loginie {login} został usunięty."
            else:
                return False, "Nieprawidłowe hasło."

        except User.DoesNotExist:
            return False, "Nie znaleziono użytkownika o podanym loginie."

