from django.http import JsonResponse
from django.views import View
from .models import DataTransaction
from datetime import datetime
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import User, Family, FamilyInvitation, JoinRequest, generate_access_code
from .forms import (
    FamilyForm,
    KidForm,
    LoginForm,
    NoFamilyUserForm,
    ConfirmPasswordForm,
    MyPasswordChangeForm,
    JoinFamilyForm,
    JoinRequestForm,
    UserForm,
    # LoginLookupForm,
)

from .services import UserService
import requests


class AllUserTransactionsView(View):
    def get(self, request, user_id):
        transactions = DataTransaction.objects.filter(id_user=user_id)

        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income) if transaction.income else None,
                'expense': float(transaction.expense) if transaction.expense else None,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'transactions': transactions_list}, safe=False)


class AllUserExpensesView(View):
    def get(self, request, user_id):
        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            expense__isnull=False
        )

        expenses_list = []
        for transaction in transactions:
            expenses_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'expense': float(transaction.expense),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'expenses': expenses_list}, safe=False)


class AllUserIncomesView(View):
    def get(self, request, user_id):
        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            income__isnull=False
        )

        incomes_list = []
        for transaction in transactions:
            incomes_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'incomes': incomes_list}, safe=False)


class UserTransactionsByDateRangeView(View):
    def get(self, request, user_id, transaction_type):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            return JsonResponse({
                'error': 'Wymagane parametry start_date i end_date w formacie YYYY-MM-DD'
            }, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        filter_params = {
            'id_user': user_id,
            'transaction_date__gte': start_date,
            'transaction_date__lte': end_date
        }

        if transaction_type == 'expenses':
            filter_params['expense__isnull'] = False
            amount_field = 'expense'
        else:  # incomes
            filter_params['income__isnull'] = False
            amount_field = 'income'

        transactions = DataTransaction.objects.filter(**filter_params)

        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                amount_field: float(getattr(transaction, amount_field)),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({transaction_type: transactions_list}, safe=False)


class AllUserTransactionsByDateRangeView(View):
    def get(self, request, user_id):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            return JsonResponse({
                'error': 'Wymagane parametry start_date i end_date'
            }, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )

        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income) if transaction.income else None,
                'expense': float(transaction.expense) if transaction.expense else None,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'transactions': transactions_list}, safe=False)


class AllTransactionsFromDateView(View):
    def get(self, request, user_id):
        start_date = request.GET.get('start_date')

        if not start_date:
            return JsonResponse({
                'error': 'Wymagany parametr start_date'
            }, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__gte=start_date
        )

        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income) if transaction.income else None,
                'expense': float(transaction.expense) if transaction.expense else None,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'transactions': transactions_list}, safe=False)


class AllTransactionsToDateView(View):
    def get(self, request, user_id):
        end_date = request.GET.get('end_date')

        if not end_date:
            return JsonResponse({
                'error': 'Wymagany parametr end_date'
            }, status=400)

        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__lte=end_date
        )

        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income) if transaction.income else None,
                'expense': float(transaction.expense) if transaction.expense else None,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'transactions': transactions_list}, safe=False)


class ExpensesFromDateView(View):
    def get(self, request, user_id):
        start_date = request.GET.get('start_date')

        if not start_date:
            return JsonResponse({
                'error': 'Wymagany parametr start_date'
            }, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__gte=start_date,
            expense__isnull=False
        )

        expenses_list = []
        for transaction in transactions:
            expenses_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'expense': float(transaction.expense),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'expenses': expenses_list}, safe=False)


class ExpensesToDateView(View):
    def get(self, request, user_id):
        end_date = request.GET.get('end_date')

        if not end_date:
            return JsonResponse({
                'error': 'Wymagany parametr end_date'
            }, status=400)

        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__lte=end_date,
            expense__isnull=False
        )

        expenses_list = []
        for transaction in transactions:
            expenses_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'expense': float(transaction.expense),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'expenses': expenses_list}, safe=False)


class IncomesFromDateView(View):
    def get(self, request, user_id):
        start_date = request.GET.get('start_date')

        if not start_date:
            return JsonResponse({
                'error': 'Wymagany parametr start_date'
            }, status=400)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__gte=start_date,
            income__isnull=False
        )

        incomes_list = []
        for transaction in transactions:
            incomes_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'incomes': incomes_list}, safe=False)


class IncomesToDateView(View):
    def get(self, request, user_id):
        end_date = request.GET.get('end_date')

        if not end_date:
            return JsonResponse({
                'error': 'Wymagany parametr end_date'
            }, status=400)

        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD'
            }, status=400)

        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            transaction_date__lte=end_date,
            income__isnull=False
        )

        incomes_list = []
        for transaction in transactions:
            incomes_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': float(transaction.income),
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        return JsonResponse({'incomes': incomes_list}, safe=False)

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


def main_menu(request):
    return render(request, 'core/menu.html')


def add_income(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('cartegory')
        print(f'Przychód: {amount} ({category})')
        return render(request, 'core/thanks.html')
    return render(request, 'core/add_income.html')

def add_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        print(f'Wydatek: {amount} ({category})')
        return render(request, 'core/thanks.html')
    return render(request, 'core/add_expense.html')


def get_supported_currencies():
    url = "https://api.frankfurter.app/currencies"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Błąd pobierania walut.")
    return response.json()


def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    url = "https://api.frankfurter.app/latest"
    params = {
        "amount": amount,
        "from": from_currency,
        "to": to_currency
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception("Błąd przeliczania waluty.")

    data = response.json()
    return data["rates"][to_currency]


def currency_converter(request):
    result = None
    error = None
    currencies = {}
    from_currency = 'PLN'  # domyślna wartość
    to_currency = ''
    amount = ''

    try:
        currencies = get_supported_currencies()
    except Exception as e:
        error = str(e)

    if request.method == 'POST':
        try:
            amount = request.POST.get('amount')
            from_currency = request.POST.get('from_currency') or 'PLN'
            to_currency = request.POST.get('to_currency')

            result = convert_currency(float(amount), from_currency, to_currency)
        except Exception as e:
            error = str(e)

    return render(request, 'core/currency_converter.html', {
        'currencies': currencies,
        'result': result,
        'error': error,
        'amount': amount,
        'from_currency': from_currency,
        'to_currency': to_currency,
    })


# def currency_converter(request):
#     result = None
#     error = None
#     currencies = {}
#
#     try:
#         currencies = get_supported_currencies()
#     except Exception as e:
#         error = str(e)
#
#     if request.method == 'POST':
#         try:
#             amount = float(request.POST.get('amount'))
#             from_currency = request.POST.get('from_currency') or 'PLN'
#             to_currency = request.POST.get('to_currency')
#
#             result = convert_currency(amount, from_currency, to_currency)
#         except Exception as e:
#             error = str(e)
#
#     return render(request, 'core/currency_converter.html', {
#         'currencies': currencies,
#         'result': result,
#         'error': error
#     })
