from django.contrib import admin
from django.urls import path
from .views import income_transaction_input, expense_transaction_input

urlpatterns = [
    path('income/', income_transaction_input , name = "income_transaction"),
    path('expense/',expense_transaction_input, name = "expense_transaction")
]