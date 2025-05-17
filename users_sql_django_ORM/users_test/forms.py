import hashlib

from django import forms
from .models import Family
from .models import User
from django.contrib.auth.hashers import make_password

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['name', 'surname', 'email', 'login', 'password', 'family', 'parent']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # parent nie jest obowiązkowe:
#         self.fields['parent'].required = False
#         # Filtrowanie rodziców (opcjonalne, np. do wyboru rodziców):
#         self.fields['parent'].queryset = User.objects.filter(parent__isnull=True)
#         self.fields['family'].empty_label = None
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.password = make_password(self.cleaned_data['password'])
#         if commit:
#             user.save()
#         return user

class UserForm(forms.ModelForm):
    family_name = forms.CharField(
        label="Family Name",
        required=True,
        help_text="Wpisz dokładną nazwę rodziny, do której chcesz dołączyć lub utwórz nową rodzinę klikając na link poniżej"
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'login', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_family_name(self):
        family_name = self.cleaned_data.get('family_name')
        try:
            family = Family.objects.get(family_name=family_name)
        except Family.DoesNotExist:
            raise forms.ValidationError(f"Rodzina o nazwie '{family_name}' nie istnieje.")
        return family_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])

        # Szukamy rodziny po nazwie i przypisujemy
        family_name = self.cleaned_data['family_name']
        user.family = Family.objects.get(family_name=family_name)

        if commit:
            user.save()
        return user

class KidForm(forms.ModelForm):
    family_name = forms.CharField(
        label="Nazwa rodziny",
        required=True,
        help_text="Wpisz dokładną nazwę rodziny, do której chcesz dołączyć"
    )
    parent = forms.CharField(
        label="Login rodzica",
        required=True,
        help_text="Wpisz login rodzica"
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'login', 'password']
        labels = {
            'name': 'Imię',
            'surname': 'Nazwisko',
            'email': 'Email',
            'login': 'Login',
            'password': 'Hasło',
            'family': 'Rodzina',
            'parent': 'Rodzic',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_family_name(self):
        family_name = self.cleaned_data['family_name']
        if not Family.objects.filter(family_name=family_name).exists():
            raise forms.ValidationError(f"Rodzina o nazwie '{family_name}' nie istnieje.")
        return family_name

    def clean_parent(self):
        parent_login = self.cleaned_data.get('parent')
        family_name = self.cleaned_data.get('family_name')

        if not parent_login:
            raise forms.ValidationError("Pole 'Login rodzica' jest wymagane.")

        # Sprawdź czy istnieje użytkownik z tym loginem, z tej rodziny i który jest rodzicem
        try:
            parent_user = User.objects.get(
                login=parent_login,
                family__family_name=family_name,
                parent__isnull=True
            )
        except User.DoesNotExist:
            raise forms.ValidationError(
                f"Rodzic z loginem '{parent_login}' nie istnieje w rodzinie '{family_name}'.  Poproś swojego rodzica o poprawne dane i sprobuj ponownie."
            )

        return parent_login  # zwracamy login, bo w save() zamienimy na obiekt

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])

        # Przypisz rodzinę
        family_name = self.cleaned_data['family_name']
        user.family = Family.objects.get(family_name=family_name)

        # Znajdź rodzica po loginie i przypisz FK
        parent_login = self.cleaned_data['parent']
        parent_user = User.objects.get(
            login=parent_login,
            family__family_name=family_name,
            parent__isnull=True
        )
        user.parent = parent_user

        if commit:
            user.save()
        return user

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['family_name']
        labels = {'family_name': 'Nazwa rodziny'}

class LoginLookupForm(forms.Form):
    login = forms.CharField(label="Login użytkownika", max_length=100)