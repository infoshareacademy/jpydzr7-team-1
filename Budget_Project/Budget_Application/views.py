from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse

from .forms import IncomeTransactionsModelForm, ExpenseTransactionsModelForm


@login_required
def income_transaction_input(request):
    if request.method == 'POST':
        form = IncomeTransactionsModelForm(request.POST)
        if form.is_valid():
            form.save()  # Zapis do bazy danych
            return redirect('income_transaction')  # Przekierowanie po zapisie
    else:
        form = IncomeTransactionsModelForm()

    return render(request, 'transaction_input.html', {'form': form})

@login_required
def expense_transaction_input(request):
    if request.method == 'POST':
        form = ExpenseTransactionsModelForm(request.POST)
        if form.is_valid():
            form.save()  # Zapis do bazy danych
            return redirect('expense_transaction')  # Przekierowanie po zapisie
    else:
        form = ExpenseTransactionsModelForm()

    return render(request, 'transaction_input.html', {'form': form})