from django import forms
from .models import Users, DataTransaction


class IncomeTransactionsModelForm(forms.ModelForm):
    class Meta:
        model = DataTransaction
        fields = ["id_user", 'data_transaction' , 'income', "description", "category", "transaction_type"]
        labels = {'data_transaction' : "Transaction date"}

class ExpenseTransactionsModelForm(forms.ModelForm):
    class Meta:
        model = DataTransaction
        fields = ["id_user", 'data_transaction' , 'expense', "description", "category", "transaction_type"]
        labels = {'data_transaction' : "Transaction date"}


