# Django built-in imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View

# Python standard library imports
from datetime import datetime

# Local imports
from .forms import (
    FamilyForm,
    KidForm,
    LoginForm,
    NoFamilyUserForm,
    ConfirmPasswordForm,
    MyPasswordChangeForm,
    JoinFamilyForm,
    JoinRequestForm,
    UserForm
)
from .models import DataTransaction, User, Family, FamilyInvitation, JoinRequest, generate_access_code, \
    FamilyTransactionView
from .services import UserService

from datetime import datetime
from django.db.models import Q
import uuid


class TransactionFilterService:
    """Serwis odpowiedzialny za filtrowanie transakcji"""

    @staticmethod
    def parse_date(date_string):
        """Parsuje datę z różnych formatów"""
        if not date_string:
            return None

        date_formats = ['%Y-%m-%d', '%m/%d/%Y']
        for date_format in date_formats:
            try:
                return datetime.strptime(date_string, date_format).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def build_transaction_query(user, transaction_type=None, category=None, date_from=None, date_to=None):
        """Buduje zapytanie dla filtrowania transakcji użytkownika"""
        query = Q(id_user=user)

        if transaction_type == 'income':
            query &= Q(income__isnull=False) & Q(income__gt=0)
        elif transaction_type == 'expense':
            query &= Q(expense__isnull=False) & Q(expense__gt=0)

        if category:
            query &= Q(category=category)

        date_from_obj = TransactionFilterService.parse_date(date_from)
        if date_from_obj:
            query &= Q(transaction_date__gte=date_from_obj)

        date_to_obj = TransactionFilterService.parse_date(date_to)
        if date_to_obj:
            query &= Q(transaction_date__lte=date_to_obj)

        return query

    @staticmethod
    def calculate_totals(transactions):
        """Oblicza sumy przychodów, wydatków i bilans"""
        total_income = sum(float(t.income or 0) for t in transactions)
        total_expense = sum(float(t.expense or 0) for t in transactions)
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_income - total_expense
        }


# === SECTION: USER & FAMILY TRANSACTION VIEWS ===
def get_unique_categories():
    """Zwraca listę unikalnych kategorii transakcji"""
    return DataTransaction.objects.values_list('category', flat=True).distinct().order_by('category')


@login_required
def filtered_transactions(request):
    """Widok filtrujący transakcje po kategorii i datach dla aktualnie zalogowanego użytkownika"""
    if not request.user.is_authenticated:
        return redirect('login')

    # Pobieranie parametrów filtrowania
    selected_category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    transaction_type = request.GET.get('type', '')

    # Budowanie zapytania przy użyciu serwisu
    query = TransactionFilterService.build_transaction_query(
        request.user, transaction_type, selected_category, date_from, date_to
    )

    transactions = DataTransaction.objects.filter(query).order_by('-transaction_date')
    totals = TransactionFilterService.calculate_totals(transactions)

    context = {
        'user': request.user,
        'user_id': request.user.user_id,
        'transactions': transactions,
        'categories': get_unique_categories(),
        'selected_category': selected_category,
        'date_from': date_from,
        'date_to': date_to,
        'transaction_type': transaction_type,
        **totals
    }

    return render(request, 'filtered_transactions.html', context)


@login_required
def filtered_family_transactions(request):
    """Widok filtrujący transakcje rodziny po kategorii, datach i członkach rodziny"""
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    if not user.family_id:
        return redirect('dashboard')

    # Pobieranie parametrów filtrowania
    selected_category = request.GET.get('category', '')
    selected_user = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    transaction_type = request.GET.get('type', '')

    # Pobieranie bazowych transakcji rodziny
    base_transactions = FamilyTransactionView.get_family_transactions(user)
    filtered_transactions = base_transactions

    # Aplikowanie filtrów
    if selected_category:
        filtered_transactions = filtered_transactions.filter(category=selected_category)

    if selected_user:
        try:
            selected_user_uuid = uuid.UUID(selected_user)
            filtered_transactions = filtered_transactions.filter(id_user__user_id=selected_user_uuid)
        except (ValueError, TypeError):
            pass

    if transaction_type == 'expense':
        filtered_transactions = filtered_transactions.filter(expense__isnull=False, expense__gt=0)
    elif transaction_type == 'income':
        filtered_transactions = filtered_transactions.filter(income__isnull=False, income__gt=0)

    # Filtrowanie dat
    date_from_obj = TransactionFilterService.parse_date(date_from)
    if date_from_obj:
        filtered_transactions = filtered_transactions.filter(transaction_date__gte=date_from_obj)

    date_to_obj = TransactionFilterService.parse_date(date_to)
    if date_to_obj:
        filtered_transactions = filtered_transactions.filter(transaction_date__lte=date_to_obj)

    transactions = filtered_transactions.order_by('-transaction_date')

    # Pobieranie danych pomocniczych
    family_members = User.objects.filter(family_id=user.family_id)
    categories = DataTransaction.objects.filter(
        id_user__in=family_members
    ).values_list('category', flat=True).distinct().order_by('category')
    categories = [cat for cat in categories if cat]

    family_members_info = User.objects.filter(family_id=user.family_id).values(
        'user_id', 'name', 'surname', 'role'
    ).order_by('name', 'surname')

    # Obliczanie sum finansowych
    totals = TransactionFilterService.calculate_totals(transactions)

    # Podsumowanie według członków rodziny
    family_summary = []
    for member in family_members_info:
        member_transactions = transactions.filter(id_user__user_id=member['user_id'])
        if member_transactions.exists():
            member_totals = TransactionFilterService.calculate_totals(member_transactions)
            family_summary.append({
                'user_name': member['name'],
                'user_surname': member['surname'],
                'user_role': member['role'],
                **member_totals
            })

    context = {
        'user': user,
        'transactions': transactions,
        'expenses_only': transactions.filter(expense__isnull=False, expense__gt=0),
        'incomes_only': transactions.filter(income__isnull=False, income__gt=0),
        'categories': categories,
        'family_members': family_members_info,
        'family_summary': family_summary,
        'selected_category': selected_category,
        'selected_user': selected_user,
        'selected_type': transaction_type,
        'date_from': date_from,
        'date_to': date_to,
        **totals
    }

    return render(request, 'filtered_family_transactions.html', context)


# ---------USERS---LOGIN---REGISTRATION------->

def generate_unique_access_code(length=6):
    while True:
        code = generate_access_code(length)
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
    if not request.session.get('welcome_shown', False):
        show_welcome = True
        request.session['welcome_shown'] = True

    user_role = request.user.role

    return render(request, 'users_test/dashboard.html', {
        'show_welcome': show_welcome,
        'role': user_role
    })


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def create_family(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            family.created_by = request.user
            family.save()

            request.user.family = family
            request.user.save()

            return render(request, "users_test/success.html", {"family": family})
    else:
        form = FamilyForm()

    return render(request, "users_test/create_family.html", {"form": form})


@login_required
def invitation(request):
    pass
    return render(request, "users_test/invitation.html", )


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

        join_requests = []
        if family and request.user == family.created_by:
            join_requests = JoinRequest.objects.filter(family=family, accepted=False)

        return render(request, 'users_test/user_detail.html', {
            'profile_user': profile_user,
            'family_id': family_id,
            'family_members': family_members,
            'requests': join_requests
        })
    else:
        return render(request, 'users_test/user_not_found.html', {'login': login})


def create_kid(request):
    if request.method == "POST":
        form = KidForm(request.POST, user=request.user)
        if form.is_valid():
            kid = form.save()
            if request.user.is_authenticated:
                return redirect('user_detail', login=request.user.login)
            else:
                return render(request, "users_test/success_user.html", {
                    "user": kid,
                    "family": kid.family,
                    "user_type": "Kid"
                })
    else:
        form = KidForm(user=request.user)

    return render(request, "users_test/create_kid.html", {"form": form})


def home(request):
    login_form = LoginForm()

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

    return render(request, "users_test/home.html", {
        "form": login_form,
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
    try:
        kid = User.objects.get(user_id=kid_id, role='kid')
        kid.is_blocked = True
        kid.save()
    except User.DoesNotExist:
        pass
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
