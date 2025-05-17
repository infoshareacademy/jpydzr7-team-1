from django.urls import path
from . import views

urlpatterns = [
    path("family/create/", views.create_family, name="create_family"),
    path("family/<uuid:family_id>/", views.family_detail, name="family_detail"),
    path("family/validate/", views.validate_family, name="validate_family"),
    path('create_user/', views.create_user, name='create_user'),
    path('success/', views.success_page, name='success_page'),
    path('success/<uuid:user_id>/', views.success_page, name='success_page'),
    path('user/<str:login>/', views.user_detail_view, name='user_detail'),
    path('delete-user/', views.delete_user_view, name='delete_user'),
    path("create_kid/", views.create_kid, name="create_kid"),
    path('', views.home, name='home'),
    path("redirect-to-user/", views.home_view, name="redirect_to_user_detail"),
    path("find_user/", views.find_user_redirect_view, name="find_user"),
]