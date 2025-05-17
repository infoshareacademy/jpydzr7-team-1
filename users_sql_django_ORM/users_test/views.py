from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from .models import Family, User
from .forms import FamilyForm, KidForm
from .services import UserService


def create_family(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save()
            return render(request, "users_test/success.html", {"family": family})
    else:
        form = FamilyForm()
    return render(request, "users_test/create.html", {"form": form})


def family_detail(request, family_id):
    family = get_object_or_404(Family, family_id=family_id)
    return render(request, "users_test/detail.html", {"family": family})


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

def success_page(request, user_id):
    user = User.objects.get(user_id=user_id)
    family = user.family

    return render(request, 'users_test/create_user.html', {
        'user': user,
        'family': family
    })


def user_detail_view(request, login):
    user = UserService.get_user_by_login(login)
    if user:
        return render(request, 'users_test/user_detail.html', {'user': user})
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
        form = KidForm(request.POST)
        if form.is_valid():
            kid = form.save()
            return render(request, "users_test/success_user.html", {
                "user": kid,
                "family": kid.family,
                "user_type": "Kid"
            })
    else:
        form = KidForm()

    return render(request, "users_test/create_kid.html", {"form": form})

from django.shortcuts import redirect

def home_view(request):
    if request.method == "POST":
        form = LoginLookupForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data["login"]
            return redirect("user_detail", login=login)
    else:
        form = LoginLookupForm()

    return render(request, "users_test/home.html", {"form": form})

def home(request):
    return render(request, "users_test/home.html")
