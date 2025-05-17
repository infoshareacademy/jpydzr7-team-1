from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views import View
from .models import DataTransaction
from datetime import datetime


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
