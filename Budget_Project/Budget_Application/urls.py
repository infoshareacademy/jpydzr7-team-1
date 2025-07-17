from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    MyPasswordResetView,
    filtered_transactions,
)

urlpatterns = [
    # ==================== STRONA GŁÓWNA ====================
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ==================== TRANSAKCJE ====================
    path('transactions/filter/', filtered_transactions, name='filtered-transactions'),
    path('transactions/family/filter/', views.filtered_family_transactions, name='filtered-family-transactions'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit-transaction'),

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

    # ==================== DODANIE TRANSAKCJI ====================
    path("add_transaction/<str:type>", views.add_transaction, name="add_transaction"),
    # ==================== DODANIE KATEGORII ====================
    path("add_category/<str:type>", views.add_category, name="add_category"),
]