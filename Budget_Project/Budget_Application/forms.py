from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Family, FamilyInvitation, User, DataTransaction, Categories
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginForm(forms.Form):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Login',
            'class': 'form-control w-100'
        })
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Hasło',
            'class': 'form-control w-100'
        })
    )
class UserForm(UserCreationForm):
    family_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nazwa rodziny',
            'class': 'form-control'
        })
    )

    access_code = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Kod dostępu',
            'class': 'form-control'
        }),
        help_text="Wprowadź kod dostępu otrzymany w zaproszeniu."
    )

    password1 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Hasło',
            'class': 'form-control'
        }),
        help_text="Hasło powinno zawierać co najmniej 8 znaków, w tym wielką literę, cyfrę i znak specjalny."
    )

    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Potwierdź hasło',
            'class': 'form-control'
        }),
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'login', 'family_name', 'access_code', 'password1', 'password2')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Imię',
                'class': 'form-control'
            }),
            'surname': forms.TextInput(attrs={
                'placeholder': 'Nazwisko',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Adres e-mail',
                'class': 'form-control'
            }),
            'login': forms.TextInput(attrs={
                'placeholder': 'Login',
                'class': 'form-control'
            }),
        }

        labels = {
            'name': '',
            'surname': '',
            'email': '',
            'login': '',
            'family_name': '',
            'access_code': '',
            'password1': '',
            'password2': '',
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control w-38'

    def clean_family_name(self):
        family_name = self.cleaned_data['family_name']
        try:
            return Family.objects.get(family_name=family_name)
        except Family.DoesNotExist:
            raise ValidationError(f"Rodzina o nazwie '{family_name}' nie istnieje.")

    def clean_access_code(self):
        code = self.cleaned_data.get('access_code')
        family = self.cleaned_data.get('family_name')

        try:
            invitation = FamilyInvitation.objects.get(access_code=code, family=family)
        except FamilyInvitation.DoesNotExist:
            raise ValidationError("Nieprawidłowy kod dostępu dla podanej rodziny.")

        if not invitation.is_valid():
            raise ValidationError("Kod dostępu jest nieaktualny lub został już użyty.")

        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        family = self.cleaned_data['family_name']
        user.family = family
        user.role = 'adult'

        if commit:
            user.save()
            try:
                group = Group.objects.get(name='Adult')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

            access_code = self.cleaned_data.get('access_code')
            invitation = FamilyInvitation.objects.get(access_code=access_code, family=family)
            invitation.accepted = True
            invitation.save()

        return user

class NoFamilyUserForm(UserCreationForm):
    password1 = forms.CharField(
        label="",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Hasło',
            'class': 'form-control'
        }),
        help_text="Hasło powinno zawierać co najmniej 8 znaków, w tym wielką literę, cyfrę i znak specjalny."
    )

    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Potwierdź hasło',
            'class': 'form-control'
        }),
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'login', 'password1', 'password2')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię', 'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Nazwisko', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Adres e-mail', 'class': 'form-control'}),
            'login': forms.TextInput(attrs={'placeholder': 'Login', 'class': 'form-control'}),
        }
        labels = {
            'name': '',
            'surname': '',
            'email': '',
            'login': '',
            'password1': '',
            'password2': '',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.family = None  # Użytkownik bez rodziny
        user.role = 'adult'  # lub 'kid' – jak wolisz

        if commit:
            user.save()
            try:
                group = Group.objects.get(name='Adult')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        return user

class KidForm(forms.ModelForm):
    family_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nazwa rodziny',
            'class': 'form-control'
        })
    )

    parent = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Login rodzica',
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Hasło dziecka',
            'class': 'form-control'
        }),
        strip=False,
        help_text="Hasło powinno zawierać co najmniej 8 znaków, w tym wielką literę, cyfrę i znak specjalny."
    )

    confirm_password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Potwierdź hasło',
            'class': 'form-control'
        }),
        strip=False,
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'login']
        labels = {field: '' for field in fields}
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Imię dziecka', 'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Nazwisko', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email dziecka lub rodzica', 'class': 'form-control'}),
            'login': forms.TextInput(attrs={'placeholder': 'Login dziecka', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super(KidForm, self).__init__(*args, **kwargs)

        # Ustawienie pól jako domyślnych dla zalogowanego użytkownika
        if self.request_user and self.request_user.is_authenticated:
            # Ustaw domyślne wartości
            self.fields['family_name'].initial = getattr(self.request_user.family, 'family_name', '')
            self.fields['parent'].initial = self.request_user.login

            self.fields['family_name'].widget = forms.HiddenInput()
            self.fields['parent'].widget = forms.HiddenInput()

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

        self.order_fields([
            'name', 'surname', 'email', 'login',
            'family_name', 'parent',
            'password', 'confirm_password'
        ])


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

        try:
            User.objects.get(
                login=parent_login,
                family__family_name=family_name,
                parent__isnull=True
            )
        except User.DoesNotExist:
            raise forms.ValidationError(
                f"Rodzic z loginem '{parent_login}' nie istnieje w rodzinie '{family_name}'."
            )

        return parent_login

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        parent_login = cleaned_data.get('parent')
        family_name = cleaned_data.get('family_name')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Hasła nie są zgodne.")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)

        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                if not (parent_login and family_name):
                    self.add_error('email', "Nie można zweryfikować adresu email bez loginu rodzica i nazwy rodziny.")
                else:
                    try:
                        parent_user = User.objects.get(
                            login=parent_login,
                            family__family_name=family_name,
                            parent__isnull=True
                        )
                        if parent_user.email != email:
                            self.add_error('email', "Ten adres email jest już przypisany do innego użytkownika.")
                    except User.DoesNotExist:
                        self.add_error('email', "Nie znaleziono rodzica do weryfikacji adresu email.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])

        # przypisz rodzinę
        family_name = self.cleaned_data['family_name']
        user.family = Family.objects.get(family_name=family_name)

        # przypisz rodzica
        parent_login = self.cleaned_data['parent']
        parent_user = User.objects.get(
            login=parent_login,
            family__family_name=family_name,
            parent__isnull=True
        )
        user.parent = parent_user
        user.role = 'kid'

        if commit:
            user.save()
            try:
                group = Group.objects.get(name='Kid')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        return user

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['family_name']
        labels = {'family_name': 'Nazwa rodziny'}


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Stare hasło', 'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Nowe hasło', 'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Powtórz nowe hasło', 'class': 'form-control'})

        self.fields['new_password1'].help_text = (
            "Hasło musi mieć co najmniej 8 znaków, zawierać dużą literę, cyfrę i znak specjalny."
        )


class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(
        label="Podaj hasło",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Podaj hasło'
        }),
        strip=False,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Hasło jest niepoprawne.")
        return password

class JoinFamilyForm(forms.Form):
    family_name = forms.CharField(
        max_length=50,
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Wprowadź nazwę rodziny do której chcesz dołączyć',
            'class': 'form-control'
        })
    )
    access_code = forms.CharField(
        max_length=6,
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Wprowadź kod dostępu',
            'class': 'form-control'
        })
    )


class JoinRequestForm(forms.Form):
    family_name = forms.CharField(
        max_length=50,
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nazwa rodziny do której chcesz dołączyć',
            'class': 'form-control'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': "Twoja wiadomość, którą chcesz dołączyć do swojej prośby",
            'rows': 4,
            'class': 'form-control'
        }),
        required=False,
        label="",
    )




class AddTransaction(forms.ModelForm):
    TYPY_TRANSAKCJI = [
        ('one off', 'jednorazowa'),
        ('monthly', 'miesięczna'),
    ]

    # Nadpisujemy pole tylko w formularzu
    transaction_type = forms.ChoiceField(
        label='Typ transakcji',
        choices=TYPY_TRANSAKCJI,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False  # jeśli pole może być puste
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # pobieramy usera z widoku
        form_type = kwargs.pop('form_type', None)
        super().__init__(*args, **kwargs)
        self.fields['id_user'].queryset = User.objects.filter(family=user.family)
        self.fields['income'].required = True
        self.fields['expense'].required = True
        self.fields['category'].queryset = Categories.objects.filter(
            category_type=form_type,
            user_id__family=user.family
        )
        self.fields['description'].required = False
        self.fields['transaction_type'].required = True
        if form_type == 'income':
            self.fields['expense'].widget = forms.HiddenInput()
            self.fields['expense'].required = False
            self.fields['income'].required = True
        elif form_type == 'expense':
            self.fields['income'].widget = forms.HiddenInput()
            self.fields['income'].required = False
            self.fields['expense'].required = True
    class Meta:
        model = DataTransaction
        fields = ['id_user','transaction_date', 'income', 'expense', 'category', 'description', 'transaction_type']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'income': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),

            # transaction_type pomijamy tutaj, bo nadpisaliśmy je wyżej
        }
        labels = {
            'id_user': 'Użytkownik',
            'transaction_date': 'Data transakcji',
            'income': 'Przychód',
            'expense': 'Wydatek',
            'category': 'Kategoria',
            'description': 'Opis (opcjonalnie)',

        }


class AddCategory(forms.ModelForm):
#TODO: dodajmy walidację na dublowanie kategorii

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # pobieramy usera z widoku
        form_type = kwargs.pop('form_type', None)
        super().__init__(*args, **kwargs)



    class Meta:
        model = Categories
        fields = ['category_name']
        widgets = {
        'category_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
        'category_name': 'Nazwa kategorii'

        }