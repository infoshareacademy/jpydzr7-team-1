from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("family/create/", views.create_family, name="create_family"),
    path("family/<uuid:family_id>/", views.family_detail, name="family_detail"),
    path("family/validate/", views.validate_family, name="validate_family"),
    path('create_user/', views.create_user, name='create_user'),
    path('create_user_no_family/', views.register_no_family_user, name='create_user_no_family'),
    path('success/', views.success_page, name='success_page'),
    path('success/<uuid:user_id>/', views.success_page, name='success_page'),
    path('user/<str:login>/', views.user_detail_view, name='user_detail'),
    path('delete-user/', views.delete_user_view, name='delete_user'),
    path("create_kid/", views.create_kid, name="create_kid"),
    path('', views.home, name='home'),
    path("redirect-to-user/", views.home, name="redirect_to_user_detail"),
    path("find_user/", views.find_user_redirect_view, name="find_user"),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_user/', views.create_user, name='create_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('invitation/', views.invitation, name='invitation'),
    path('remind_password/', views.remind_password, name='remind_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('kid/<uuid:kid_id>/block/', views.block_kid, name='block_kid'),
    path('kid/<uuid:kid_id>/unblock/', views.unblock_kid, name='unblock_kid'),
    path('password_change/', views.change_password, name='password_change'),
]

