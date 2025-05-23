import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UppercaseSpecialCharDigitValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Hasło musi zawierać co najmniej jedną wielką literę."),
                code='password_no_upper',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Hasło musi zawierać co najmniej jeden znak specjalny."),
                code='password_no_special',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Hasło musi zawierać co najmniej jedną cyfrę."),
                code='password_no_digit',
            )

    def get_help_text(self):
        return _(
            "Hasło musi zawierać co najmniej jedną wielką literę, jeden znak specjalny i jedną cyfrę."
        )