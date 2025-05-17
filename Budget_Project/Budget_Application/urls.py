from django.urls import path
from .views import (
    AllUserTransactionsView,
    AllUserExpensesView,
    AllUserIncomesView,
    AllUserTransactionsByDateRangeView,
    AllTransactionsFromDateView,
    AllTransactionsToDateView,
    ExpensesFromDateView,
    ExpensesToDateView,
    IncomesFromDateView,
    IncomesToDateView,
    UserTransactionsByDateRangeView
)


urlpatterns = [
    path('transactions/user/<int:user_id>/', AllUserTransactionsView.as_view(), name='all-user-transactions'),
    path('transactions/user/<int:user_id>/expenses/', AllUserExpensesView.as_view(), name='all-user-expenses'),
    path('transactions/user/<int:user_id>/incomes/', AllUserIncomesView.as_view(), name='all-user-incomes'),
    path('transactions/user/<int:user_id>/<str:transaction_type>/by-date/',
         UserTransactionsByDateRangeView.as_view(), name='user-transactions-by-daterange'),
    path('transactions/user/<int:user_id>/date-range/', AllUserTransactionsByDateRangeView.as_view(),
         name='all-user-transactions-date-range'),
    path('transactions/user/<int:user_id>/from-date/', AllTransactionsFromDateView.as_view(), name='transactions-from-date'),
    path('transactions/user/<int:user_id>/to-date/', AllTransactionsToDateView.as_view(), name='transactions-to-date'),
    path('transactions/user/<int:user_id>/expenses/start-date/', ExpensesFromDateView.as_view(), name='expenses-from-date'),
    path('transactions/user/<int:user_id>/expenses/end-date/', ExpensesToDateView.as_view(), name='expenses-to-date'),
    path('transactions/user/<int:user_id>/incomes/start-date/', IncomesFromDateView.as_view(), name='incomes-from-date'),
    path('transactions/user/<int:user_id>/incomes/end-date/', IncomesToDateView.as_view(), name='incomes-to-date'),
]
