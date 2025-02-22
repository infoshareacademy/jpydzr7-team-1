import os

import pandas as pd
from datetime import datetime


class HomeBudget:

    @staticmethod
    def home_budget_update(amount, type, frequency, assigned_user, category, description, month, user):
        data = {
            'Amount': [amount],  # Zmienione na listę, aby było w jednej kolumnie
            'Type': [type],
            'Frequency': [frequency],
            'Assigned_User': [assigned_user],
            'Category': [category],
            'Description': [description],
            'Month': [month],
            "User" : [user],
            'Time': [datetime.now()]  # Data i godzina w czasie wywołania
        }
        file_path = 'tabela1.xlsx'
        df = pd.DataFrame(data)
        headers = ["Amount", "Type", "Frequency", "Assinged_User", "Category","Description", "Month", "User", "Time"]
        if not os.path.exists(file_path):
            # Jeśli plik nie istnieje, zapisujemy dane z nagłówkami
            df.to_excel(file_path, index=False, header=headers)
        else:
            # Jeśli plik już istnieje, dodajemy dane do istniejącego pliku
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=headers, sheet_name='Sheet1')  # Dodanie nowych danych bez nagłówków



def update (choice, user):
    amount = input('Podaj kwotę:  ')
    print('''Wybierz typ:
    [1] przychód
    [2] wydatek''')
    _ = input()
    if _ == "1":
        type = "income"
    elif _ == "2":
        type = "expense"
    print('''Wybierz czestotliwośc:
    [1] jednorazowy
    [2] miesięczny''')
    _ = input()
    if _ == "1":
        frequency = "unique"
    elif _ == "2":
        frequency = "monthly"
    print('''Wybierz użytkownika do którego chcesz przypisać tą pozycję:''')
    print(users)
    _ = input()
    assigned_user = users[_]
    category =""
    if type == "expense":
        print("Wybierz kategoię:")
        print(expense_categories)
        _ = input()
        category = expense_categories[_]
    print("Podaj opis albo wciśnij Enter aby pominąć")
    description = input()
    current_date = datetime.now()
    month_name = current_date.strftime("%B")
    month = month_name
    HomeBudget.home_budget_update(amount,type,frequency,assigned_user,category,description,month,user)

user = "Adrian"
users = {"1": "Adam", "2": "Marta"}
expense_categories = {"1": "Jedzenie", "2": "Rozrywka"}
update(1, user)
# class BudgetPlan(HomeBudget):
#     def __init__(self, category, category_expense):
#         self.category_name = category
#         self.category_expense = category_expense
#         pass
#
#     def __str__(self):
#         return f"{self.category_name}, {self.category_expense}"
#
# class Income:
#     def __init__(self, user, source, amount):
#         self.income = user
#         self.source = source
#         self.amount = amount

        # pass

# def budget_plan():
#     monthly_income = 0
#     print("Plan miesięcznych przychodów:")
#     more = True
#     while more:
#         print("Podaj opis")
#         income_title = input()
#         print("Podaj kwotę")
#         income_amount = int(input())
#         Income(user, income_title, income_amount)
#         print("Dodać kolejny? Y/N")
#         if input().upper() == "N":
#             more = False
#         else:
#             pass
#         monthly_income += income_amount


    #
    #
    # monthly_expenses = 0
    # print("Plan wydatków miesięcznych w poszczególnych kategoriach:")
    # for category in list_of_categories:
    #     print(f"Podaj przewidywane miesięczne wydatki z kategorii {category}")
    #     category_expense = int(input())
    #     category_obj = BudgetCategory(category, category_expense)
    #     list_of_cat_objects.append(category_obj)
    #     monthly_expenses += category_expense
    #
    # HomeBudget(monthly_income, monthly_expenses)
    # print(f"Miesieczny przychod to {monthly_income},miesieczne wydatki to {monthly_expenses}")



# user = "Adrian"
# list_of_categories= ["Jedzenie w domu", "Jedzenie na mieście", "Rozrywka"]
# list_of_cat_objects = []
# print("Zaplanuj budzet")
# budget_plan()

# "1. Dodanie przychodów do budżetu\n"
# "2. Odejmowanie wydatków od budżetu\n"
# "3. Dodanie stałych/cyklicznych wydatków\n"
# "4. Export raportu di pliku\n"
# "5. Przeliczenie Walut\n"
# "6. Historia Wydatków\n"
# "0. Wyjście z Aplikacji")