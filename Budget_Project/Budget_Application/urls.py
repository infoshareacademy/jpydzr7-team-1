from django.contrib import admin
from django.urls import path
from .views import income_transaction_input, expense_transaction_input
from  .models import Users

urlpatterns = [
    path('income/<int:id_user>/', income_transaction_input , name = "income_transaction"),
    path('expense/<int:id_user>/',expense_transaction_input, name = "expense_transaction")
]