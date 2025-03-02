import os
#from time import strptime
import dummy_data
import budget_manager
from datetime import datetime




def take_input(type):
    _ = input('Podaj kwotę:  ')
    amount = float(_)
    print('''Wybierz częstotliwość:
    [1] jednorazowy
    [2] miesięczny''')
    _ = input()
    if _ == "1":
        frequency = "Jednorazowy"
    elif _ == "2":
        frequency = "Miesieczny"

#TODO: dodanie kolumny przypisanego uzytkownika do tabeli
    print('''Wybierz użytkownika do którego chcesz przypisać tą pozycję:''')
    print(dummy_data.users)
    _ = input()
    assigned_user = dummy_data.users[_]
    category = ""

    print("Wybierz kategoię:")
    if type == "income":
        print(dummy_data.income_categories)
        _ = input()
        category = dummy_data.income_categories[_]
    elif type == "expense":
        print(dummy_data.expense_categories)
        _ = input()
        category = dummy_data.expense_categories[_]

    print("Podaj opis albo wciśnij Enter aby pominąć")
    description = input()

    print("Podaj datę jeśli inna niż dzisiejsza (DD.MM.YYYY) lub wciśnij enter :")
    _ = input()
#TODO: zmiana formatu daty w pliku excel na europejski "%d.%m.%Y"
    if not _ == "":
        date = datetime.strptime(_, "%d.%m.%Y")
        date.strftime("%Y-%m-%d")
    else:
        date = None

    budget = budget_manager.BudgetManager()
    if type == "income":
        budget.add_income(dummy_data.user_id, amount, date, description, category, frequency)
    elif type == "expense":
        budget.add_expense(dummy_data.user_id, amount, date, description, category, frequency)
