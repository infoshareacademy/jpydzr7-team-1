import os
#from time import strptime
import dummy_data
import budget_manager
from datetime import datetime


def user_input_and_validation(test_number):
    verification_pass = False
    while not verification_pass:
        value = input()
        if test_number == 1:
            try:
                return float(value)
            except ValueError:
                pass
        elif test_number == 2:
            if value == "1":
                return "Jednorazowy"
            elif value == "2":
                return "Miesięczny"
        elif test_number == 3:
            if value in dummy_data.users.keys():
                return value
        elif test_number == 4:
            if value in dummy_data.income_categories.keys():
                return value
        elif test_number == 5:
            if value in dummy_data.expense_categories.keys():
                return value
        elif test_number == 6:
            if not value:
                return None
            else:
                return value
        elif test_number == 7:
            if not value:
                return None
            try:
                date = datetime.strptime(value, "%d.%m.%Y")
                date = date.strftime("%d.%m.%Y")
                return date
            except ValueError:
                pass
        print("Podaj właściwą wartość.")


def take_input(transaction_type):

    print('Podaj kwotę: ')
    amount = user_input_and_validation(1)

    print('''Wybierz częstotliwość:
    [1] jednorazowy
    [2] miesięczny''')
    frequency = user_input_and_validation(2)

    print('''Wybierz użytkownika do którego chcesz przypisać tą pozycję: ''')
    print(dummy_data.users)
    _ = user_input_and_validation(3)
    assigned_user = dummy_data.users[_]

    category = ""
    print("Wybierz kategorię: ")
    if transaction_type == "income":
        print(dummy_data.income_categories)
        _ = user_input_and_validation(4)
        category = dummy_data.income_categories[_]
    elif transaction_type == "expense":
        print(dummy_data.expense_categories)
        _ = user_input_and_validation(5)
        category = dummy_data.expense_categories[_]

    print("Podaj opis albo wciśnij Enter aby pominąć: ")
    description = user_input_and_validation(6)

    print("Podaj datę jeśli inna niż dzisiejsza (DD.MM.YYYY) lub wciśnij enter: ")
    date = user_input_and_validation(7)
    #TODO: zmiana formatu daty w pliku excel na europejski "%d.%m.%Y"

    budget = budget_manager.BudgetManager()
    if transaction_type == "income":
        budget.add_income(dummy_data.user_id, amount, date, description, category, frequency)
    elif transaction_type == "expense":
        budget.add_expense(dummy_data.user_id, amount, date, description, category, frequency)
