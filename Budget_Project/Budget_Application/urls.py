from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
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
    UserTransactionsByDateRangeView,
    MyPasswordResetView,
    filtered_transactions
)

urlpatterns = [
    # ==================== STRONA GŁÓWNA ====================
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ==================== TRANSAKCJE ====================
    path('transactions/', AllUserTransactionsView.as_view(), name='all-user-transactions'),
    path('expenses/', AllUserExpensesView.as_view(), name='expenses'),
    path('incomes/', AllUserIncomesView.as_view(), name='all-user-incomes'),
    path('transactions/filter/', filtered_transactions, name='filtered-transactions'),

    # Transakcje według dat
    path('transactions/<str:transaction_type>/by-date/',
         UserTransactionsByDateRangeView.as_view(), name='user-transactions-by-daterange'),
    path('transactions/user/<int:user_id>/date-range/',
         AllUserTransactionsByDateRangeView.as_view(), name='all-user-transactions-date-range'),
    path('transactions/user/<int:user_id>/from-date/',
         AllTransactionsFromDateView.as_view(), name='transactions-from-date'),
    path('transactions/user/<int:user_id>/to-date/',
         AllTransactionsToDateView.as_view(), name='transactions-to-date'),

    # Wydatki według dat
    path('transactions/user/<int:user_id>/expenses/start-date/',
         ExpensesFromDateView.as_view(), name='expenses-from-date'),
    path('transactions/user/<int:user_id>/expenses/end-date/',
         ExpensesToDateView.as_view(), name='expenses-to-date'),

    # Dochody według dat
    path('transactions/user/<int:user_id>/incomes/start-date/',
         IncomesFromDateView.as_view(), name='incomes-from-date'),
    path('transactions/user/<int:user_id>/incomes/end-date/',
         IncomesToDateView.as_view(), name='incomes-to-date'),

    # ==================== UŻYTKOWNICY ====================
    path('user/<str:login>/', views.user_detail_view, name='user_detail'),
    path('create_user/', views.create_user, name='create_user'),
    path('create_user_no_family/', views.register_no_family_user, name='create_user_no_family'),
    path('success/<uuid:user_id>/', views.success_page, name='success_page'),
    path('delete-account/', views.delete_account, name='delete_account'),

    # ==================== AUTORYZACJA ====================
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', views.change_password, name='password_change'),

    # Reset hasła
    path('remind_password/', MyPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users_test/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users_test/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users_test/password_reset_complete.html'),
         name='password_reset_complete'),

    # ==================== RODZINA ====================
    path("family/create/", views.create_family, name="create_family"),
    path('join_family/', views.join_family_view, name='join_family'),
    path('join_family_request/', views.join_family_request_view, name='join_family_request'),
    path('join_requests/', views.view_join_requests, name='join_requests'),
    path('invitation/', views.invitation_fun, name='invitation'),

    # ==================== DZIECI ====================
    path("create_kid/", views.create_kid, name="create_kid"),
    path('kid/<uuid:kid_id>/block/', views.block_kid, name='block_kid'),
    path('kid/<uuid:kid_id>/unblock/', views.unblock_kid, name='unblock_kid'),
]