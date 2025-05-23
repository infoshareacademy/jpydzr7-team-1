from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from .models import Family, User
from .forms import FamilyForm, KidForm, LoginForm, NoFamilyUserForm, ConfirmPasswordForm, MyPasswordChangeForm
from .services import UserService
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm, LoginLookupForm
from .models import User, Family
from django.http import HttpResponseForbidden
from functools import wraps

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
    user_role = request.user.role  # 'adult' albo 'kid'
    return render(request, 'users_test/dashboard.html', {'role': user_role})



def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def create_family(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save()
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

def remind_password(request):
    pass
    return render(request, "users_test/remind_password.html", )


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


from django.shortcuts import render

from .forms import UserForm

# def custom_login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             login_input = form.cleaned_data['login']
#             password = form.cleaned_data['password']
#             user = authenticate(request, login=login_input, password=password)
#             if user:
#                 login(request, user)
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, "Nieprawidłowy login lub hasło.")
#     else:
#         form = LoginForm()

    # return render(request, 'users_test/login.html', {'form': form})

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


def user_detail_view(request, login):
    profile_user = UserService.get_user_by_login(login)
    if profile_user:
        family = profile_user.family
        family_id = family.family_id if family else None
        family_members = User.objects.filter(family=family).exclude(user_id=profile_user.user_id) if family else []

        return render(request, 'users_test/user_detail.html', {
            'profile_user': profile_user,
            'family_id': family_id,
            'family_members': family_members
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