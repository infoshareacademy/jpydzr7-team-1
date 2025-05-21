from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from .models import DataTransaction, Users
from datetime import datetime


class AllUserTransactionsView(View):
    def get(self, request, user_id):
        """
        Handles the retrieval, processing, and rendering of transaction data for a specific user,
        which includes filtering, sorting, and calculating financial summaries such as income,
        expenses, and balance. Additionally, it prepares data for rendering in a web-based table.
        """
        # Pobiera parametr sortowania z URLa
        sort_order = request.GET.get('sort', 'date_desc')

        # Pobiera wszystkie transakcje z DB dla danego userid
        transactions = DataTransaction.objects.filter(id_user=user_id)

        # Sortuje zgodnie z parametrem
        if sort_order == 'date_asc':
            transactions = transactions.order_by('transaction_date')
        else:
            transactions = transactions.order_by('-transaction_date')

        transactions_list = []
        total_income = 0
        total_expense = 0

        for transaction in transactions:
            income = float(transaction.income) if transaction.income else None
            expense = float(transaction.expense) if transaction.expense else None

            # Oblicza sumy dla przychodów i wydatków
            if income:
                total_income += income
            if expense:
                total_expense += expense

            transactions_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': income,
                'expense': expense,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        # Oblicza bilans całkowity
        total_balance = total_income - total_expense

        # Pobiera unikalne kategorie
        categories = get_unique_categories()

        context = {
            'transactions': transactions_list,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_balance': total_balance,
            'user_id': user_id,
            'sort_order': sort_order,
            'categories': categories,
            'selected_category': ''  # Domyślnie wyświetlamy transakcje dla wszystkich kat dla tego widoku
        }

        return render(request, 'transactions_all.html', context)


class AllUserExpensesView(View):
    """
    Provides functionality to retrieve, process, and render expense transaction
    data for a given user. This includes calculating the total expenditures,
    preparing a list of individual transactions, and retrieving unique
    transaction categories. It renders the data to the specified template
    for display.
    """
    def get(self, request, user_id):
        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            expense__gt=0
        )

        #Debagowanie
        #print(f"Znaleziono {transactions.count()} wydatków dla użytkownika {user_id}")

        expenses_list = []
        total_expense = 0

        for transaction in transactions:
            expense = float(transaction.expense) if transaction.expense else 0
            total_expense += expense

            expenses_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'expense': expense,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        categories = get_unique_categories()

        context = {
            'transactions': expenses_list,
            'total_expense': total_expense,
            'user_id': user_id,
            'categories': categories,
            'selected_category': ''
        }

        return render(request, 'expenses.html', context)


class AllUserIncomesView(View):
    """
    This view is responsible for fetching all transactions related to incomes
    for a given user, processing them, and rendering the corresponding HTML
    template with the data. The data passed to the template includes the
    list of income transactions, their details, the total income, and other
    contextual information like available categories.
    """
    def get(self, request, user_id):
        transactions = DataTransaction.objects.filter(
            id_user=user_id,
            income__gt=0
        )

        # Debugowanie
        #print(f"Znaleziono {transactions.count()} przychodów dla użytkownika {user_id}")

        incomes_list = []
        total_income = 0

        for transaction in transactions:
            income = float(transaction.income) if transaction.income else 0
            total_income += income

            incomes_list.append({
                'transaction_id': transaction.transaction_id,
                'transaction_date': transaction.transaction_date,
                'income': income,
                'description': transaction.description,
                'category': transaction.category,
                'transaction_type': transaction.transaction_type
            })

        categories = get_unique_categories()

        context = {
            'transactions': incomes_list,
            'total_income': total_income,
            'user_id': user_id,
            'categories': categories,
            'selected_category': ''
        }

        return render(request, 'incomes.html', context)


def get_unique_categories():
    """
    This function queries the `DataTransaction` model to extract and
    return a list of all unique categories, ordered in ascending order.
    The result is constructed as a flat list for ease of use.

    :return: List of unique, distinct category names in ascending order
    """
    return DataTransaction.objects.values_list('category', flat=True).distinct().order_by('category')



def filtered_transactions(request, user_id):
    """Widok filtrujący transakcje po kategorii i datach"""
    from datetime import datetime
    from django.db.models import Q

    user = Users.objects.get(user_id=user_id)
    selected_category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Podstawowe zapytanie
    query = Q(id_user=user_id)

    # Dodanie filtra kategorii, jeśli została wybrana
    if selected_category:
        query &= Q(category=selected_category)

    # Dodanie filtra dat, jeśli zostały wybrane
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%m/%d/%Y').date()
        query &= Q(transaction_date__gte=date_from_obj)

    if date_to:
        date_to_obj = datetime.strptime(date_to, '%m/%d/%Y').date()
        query &= Q(transaction_date__lte=date_to_obj)

    transactions = DataTransaction.objects.filter(query).order_by('-transaction_date')
    categories = get_unique_categories()

    # Obliczanie sum i bilansu
    total_income = sum(float(t.income or 0) for t in transactions)
    total_expense = sum(float(t.expense or 0) for t in transactions)
    total_balance = total_income - total_expense

    # Debug
    print(f"Query: {query}")
    # print(f"Data od: {date_from}, Data do: {date_to}")
    # print(f"Liczba znalezionych transakcji: {transactions.count()}")

    context = {
        'user': user,
        'user_id': user_id,
        'transactions': transactions,
        'categories': categories,
        'selected_category': selected_category,
        'date_from': date_from,
        'date_to': date_to,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance,
    }
    return render(request, 'filtered_transactions.html', context)


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


def get_unique_categories():
    return DataTransaction.objects.values_list('category', flat=True).distinct().order_by('category')



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
