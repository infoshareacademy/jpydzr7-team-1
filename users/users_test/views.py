from django.contrib.sites import requests
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from .models import Family, User, JoinRequest
from .forms import FamilyForm, KidForm, LoginForm, NoFamilyUserForm, ConfirmPasswordForm, MyPasswordChangeForm, \
    JoinFamilyForm, JoinRequestForm
from .services import UserService
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm, LoginLookupForm
from .models import User, Family
from django.http import HttpResponseForbidden
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings
from .models import FamilyInvitation, Family
from .models import generate_access_code
from django.contrib.auth.views import PasswordResetView

from django.urls import reverse_lazy

from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render

from .forms import UserForm


def generate_unique_access_code(length=6):
    while True:
        code = generate_access_code(length)  # zakładam, że ta funkcja generuje losowy kod
        if not FamilyInvitation.objects.filter(access_code=code).exists():
            return code

@login_required
def invitation_fun(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = request.user
        family = user.family

        if not family:
            messages.error(request, 'Nie należysz do żadnej rodziny.')
        else:
            access_code = generate_unique_access_code()
            FamilyInvitation.objects.create(
                email=email,
                family=family,
                invited_by=user,
                access_code=access_code
            )
            send_mail(
                subject="Zaproszenie do rodziny w BudżetDomowy",
                message=f"Cześć!\n\nZostałeś zaproszony do rodziny '{family.family_name}'.\n"
                        f"Twój kod dostępu to: {access_code}\n\n"
                        f"Przejdź na stronę rejestracji i wpisz ten kod, aby dołączyć.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, f"Zaproszenie wysłane na adres: {email}. Kod dostępu: {access_code}")
        return redirect('invitation')

    return render(request, 'users_test/invitation.html')


def adult_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # lub inna nazwa Twojej strony logowania
        if request.user.role != 'adult':
            return HttpResponseForbidden("Brak uprawnień - dostęp tylko dla dorosłych.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def custom_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if getattr(user, 'is_blocked', False):
                    messages.error(request, "Twoje konto jest zablokowane. Skontaktuj się ze swoim rodzicem")
                else:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, "Nieprawidłowy login lub hasło.")
    else:
        form = LoginForm()

    return render(request, 'users_test/login.html', {'form': form})




@login_required
def dashboard(request):
    show_welcome = False

    # Sprawdzenie, czy powitanie było już pokazane w sesji
    if not request.session.get('welcome_shown', False):
        show_welcome = True
        request.session['welcome_shown'] = True

    user_role = request.user.role  # np. 'adult' lub 'kid'

    return render(request, 'users_test/dashboard.html', {
        'show_welcome': show_welcome,
        'role': user_role
    })

def logout_view(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def create_family(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            # utwórz obiekt, ale nie zapisuj jeszcze do bazy
            family = form.save(commit=False)
            family.created_by = request.user  # ustaw twórcę
            family.save()  # teraz zapisz z created_by

            # przypisz rodzinę użytkownikowi
            request.user.family = family
            request.user.save()

            return render(request, "users_test/success.html", {"family": family})
    else:
        form = FamilyForm()

    return render(request, "users_test/create.html", {"form": form})



def family_detail(request, family_id):
    family = get_object_or_404(Family, family_id=family_id)
    return render(request, "users_test/detail.html", {"family": family})

@login_required
def edit_profile(request):
    pass
    return render(request, "users_test/edit_profile.html", )

@login_required
def invitation(request):
    pass
    return render(request, "users_test/invitation.html", )

# def remind_password(request):
#     pass
#     return render(request, "users_test/remind_password.html", )


def validate_family(request):
    if request.method == "POST":
        family_id = request.POST.get("family_id")
        try:
            family = Family.objects.get(family_id=family_id)
            return render(request, "users_test/detail.html", {"family": family})
        except (ValueError, ValidationError):
            return render(request, "users_test/not_found.html", {"error": "Nieprawidłowy format ID."})
        except Family.DoesNotExist:
            return render(request, "users_test/not_found.html", {"family_id": family_id})
    return render(request, "users_test/validate.html")



def create_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user=form.save()
            family = user.family
            return render(request,'users_test/success_user.html', {
        'user': user,
        'family': family
    })
    else:
        form = UserForm()
    return render(request, 'users_test/create_user.html', {'form': form})

def register_no_family_user(request):
    if request.method == "POST":
        form = NoFamilyUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return render(request, 'users_test/success_user.html', {
                'user': user,
            })
    else:
        form = NoFamilyUserForm()
    return render(request, 'users_test/create_user_no_family.html', {'form': form})

def success_page(request, user_id):
    user = User.objects.get(user_id=user_id)
    family = user.family

    return render(request, 'users_test/create_user.html', {
        'user': user,
        'family': family
    })


@login_required
def user_detail_view(request, login):
    profile_user = UserService.get_user_by_login(login)
    if profile_user:
        family = profile_user.family
        family_id = family.family_id if family else None
        family_members = User.objects.filter(family=family).exclude(user_id=profile_user.user_id) if family else []

        # Tylko jeśli aktualnie zalogowany użytkownik jest twórcą tej rodziny
        join_requests = []
        if family and request.user == family.created_by:
            join_requests = JoinRequest.objects.filter(family=family, accepted=False)

        return render(request, 'users_test/user_detail.html', {
            'profile_user': profile_user,
            'family_id': family_id,
            'family_members': family_members,
            'requests': join_requests  # <-- przekazujemy do template'u
        })
    else:
        return render(request, 'users_test/user_not_found.html', {'login': login})



def find_user_redirect_view(request):
    login = request.GET.get('login')
    if login:
        return redirect('user_detail', login=login)
    return render(request, 'users_test/user_not_found.html', {'login': login})
def delete_user_view(request):
    message = None

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        success, message = UserService.remove_user_by_login_and_password(login, password)

    return render(request, 'users_test/delete_user.html', {'message': message})



def create_kid(request):
    if request.method == "POST":
        form = KidForm(request.POST, user=request.user)
        if form.is_valid():
            kid = form.save()
            if request.user.is_authenticated:
                return redirect('user_detail', login=request.user.login)  # zalogowany rodzic
            else:
                return render(request, "users_test/success_user.html", {
                    "user": kid,
                    "family": kid.family,
                    "user_type": "Kid"
                })
    else:
        form = KidForm(user=request.user)

    return render(request, "users_test/create_kid.html", {"form": form})

from django.shortcuts import redirect

def home(request):
    login_form = LoginForm()
    lookup_form = LoginLookupForm()

    # Jeśli POST dotyczy logowania
    if request.method == 'POST' and 'username' in request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Nieprawidłowy login lub hasło.")

    # Jeśli POST dotyczy wyszukiwania użytkownika po loginie
    elif request.method == 'POST' and 'login' in request.POST:
        lookup_form = LoginLookupForm(request.POST)
        if lookup_form.is_valid():
            login_value = lookup_form.cleaned_data["login"]
            return redirect("user_detail", login=login_value)

    return render(request, "users_test/home.html", {
        "form": login_form,
        "lookup_form": lookup_form
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = ConfirmPasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.delete()
            return redirect('home')  # lub inna strona po usunięciu konta
    else:
        form = ConfirmPasswordForm(request.user)
    return render(request, 'users_test/delete_account.html', {'form': form})
@login_required
def block_kid(request, kid_id):
    # kid_id jest UUID, więc możesz szukać usera po user_id
    try:
        kid = User.objects.get(user_id=kid_id, role='kid')
        # logika blokowania konta dziecka
        kid.is_blocked = True
        kid.save()
        # przekierowanie lub inna odpowiedź
    except User.DoesNotExist:
        # obsługa braku użytkownika
        pass
    # np. redirect
    return redirect('user_detail', login=request.user.login)
@login_required
def unblock_kid(request, kid_id):
    try:
        kid = User.objects.get(user_id=kid_id, role='kid')
        kid.is_blocked = False
        kid.save()
    except User.DoesNotExist:
        pass
    return redirect('user_detail', login=request.user.login)

@login_required
def change_password(request):
    form = MyPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostalo zmienione.')
            return redirect('password_change')
        else:
            messages.error(request, 'Popraw błędy w formularzu.')
    return render(request, 'users_test/password_change.html', {'form': form})

@login_required
def join_family_view(request):
    join_form = JoinFamilyForm(request.POST or None)

    if request.method == 'POST':
        if join_form.is_valid():
            code = join_form.cleaned_data['access_code']
            family_name = join_form.cleaned_data['family_name']
            try:
                invitation = FamilyInvitation.objects.get(access_code=code)
                if not invitation.is_valid():
                    messages.error(request, "Kod wygasł lub został już użyty.")
                elif request.user.family:
                    messages.error(request, "Już należysz do rodziny.")
                elif invitation.family.family_name != family_name:
                    messages.error(request, "Nazwa rodziny nie zgadza się z zaproszeniem.")
                else:
                    request.user.family = invitation.family
                    request.user.save()
                    invitation.accepted = True
                    invitation.save()
                    messages.success(request, f"Dołączyłeś do rodziny: {invitation.family.family_name}")
            except FamilyInvitation.DoesNotExist:
                messages.error(request, "Nieprawidłowy kod dostępu.")

    return render(request, 'users_test/join_family.html', {
        'join_form': join_form
    })
@login_required
def join_family_request_view(request):
    request_form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        if request_form.is_valid():
            if request.user.family:
                messages.error(request, "Już należysz do rodziny.")
            else:
                family_name = request_form.cleaned_data['family_name']
                message_text = request_form.cleaned_data['message']
                try:
                    family = Family.objects.get(family_name=family_name)
                    JoinRequest.objects.create(
                        user=request.user,
                        family=family,
                        message=message_text)

                    messages.success(request, f"Wysłano prośbę o dołączenie do rodziny: {family_name}. Poczekaj, aż administrator zaakceptuje Twoją prośbę.")
                except Family.DoesNotExist:
                    messages.error(request, "Taka rodzina nie istnieje.")

    return render(request, 'users_test/join_family_request.html', {
        'request_form': request_form
    })


@login_required
def view_join_requests(request):
    if not request.user.family:
        messages.error(request, "Nie należysz do żadnej rodziny.")
        return redirect('dashboard')

    family = request.user.family

    # 🛡️ Sprawdzenie, czy użytkownik jest administratorem tej rodziny
    if family.created_by != request.user:
        return HttpResponseForbidden("Tylko administrator rodziny może zarządzać prośbami.")

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        try:
            join_request = JoinRequest.objects.get(id=request_id, family=family, accepted=False)
        except JoinRequest.DoesNotExist:
            messages.error(request, "Nieprawidłowa prośba.")
        else:
            if action == 'accept':
                join_request.user.family = join_request.family
                join_request.user.save()
                join_request.accepted = True
                join_request.save()
                messages.success(request, f"{join_request.user} został przyjęty do Twojej rodziny.")
            elif action == 'reject':
                join_request.delete()
                messages.info(request, f"Prośba od {join_request.user} została odrzucona.")
        return redirect('user_detail', login=request.user.login)

    requests = JoinRequest.objects.filter(family=family, accepted=False)

    return render(request, 'users_test/user_detail.html', {
        'requests': requests
    })


class MyPasswordResetView(PasswordResetView):
    template_name = 'users_test/remind_password.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

