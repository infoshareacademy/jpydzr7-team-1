import pandas as pd
import uuid
from datetime import datetime
import os
from transaction_analyzer import TransactionHistoryAnalyzer


class BudgetManager:
    USER_ID_COLUMN = 'ID_urzytkownika'
    INCOME_COLUMN = 'Przychod'
    EXPENSE_COLUMN = 'Wydatek'
    DATE_COLUMN = 'Data'
    DEFAULT_COLUMNS = ['ID', USER_ID_COLUMN, DATE_COLUMN, INCOME_COLUMN, EXPENSE_COLUMN, 'Opis', 'Kategoria']

    def __init__(self, file_path="data.xlsx"):
        self.file_path = file_path
        # Inicjalizacja pliku Excel, jeśli nie istnieje
        if not os.path.exists(file_path):
            self._initialize_excel_file()

        # Utworzenie instancji TransactionHistoryAnalyzer do filtrowania danych
        self.analyzer = TransactionHistoryAnalyzer(file_path)

    def _initialize_excel_file(self):
        df = pd.DataFrame(columns=self.DEFAULT_COLUMNS)
        df.to_excel(self.file_path, index=False)

    def _get_next_id(self):
        df = pd.read_excel(self.file_path)
        if df.empty:
            return 1
        return df['ID'].max() + 1

    def _save_to_excel(self, data):
        df = pd.read_excel(self.file_path)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel(self.file_path, index=False)

    def add_expense(self, user_id: uuid.UUID, amount: float, date: str = None,
                    description: str = None, category: str = None):
        if not isinstance(user_id, uuid.UUID):
            raise ValueError("ID_urzytkownika musi być typu UUID")
        if amount <= 0:
            raise ValueError("Kwota wydatku musi być większa od 0")

        current_date = date if date else datetime.now().strftime("%Y-%m-%d")

        expense_data = {
            'ID': self._get_next_id(),
            self.USER_ID_COLUMN: str(user_id),
            self.DATE_COLUMN: current_date,
            self.INCOME_COLUMN: 0.0,
            self.EXPENSE_COLUMN: amount,
            'Opis': description if description else '',
            'Kategoria': category if category else ''
        }

        self._save_to_excel(expense_data)
        return expense_data

    def add_income(self, user_id: uuid.UUID, amount: float, date: str = None,
                   description: str = None, category: str = None):
        if not isinstance(user_id, uuid.UUID):
            raise ValueError("ID_urzytkownika musi być typu UUID")
        if amount <= 0:
            raise ValueError("Kwota przychodu musi być większa od 0")

        current_date = date if date else datetime.now().strftime("%Y-%m-%d")

        income_data = {
            'ID': self._get_next_id(),
            self.USER_ID_COLUMN: str(user_id),
            self.DATE_COLUMN: current_date,
            self.INCOME_COLUMN: amount,
            self.EXPENSE_COLUMN: 0.0,
            'Opis': description if description else '',
            'Kategoria': category if category else ''
        }

        self._save_to_excel(income_data)
        return income_data


if __name__ == "__main__":
    # TEST DATA
    # Tworzenie instancji testowego budżetu
    test_budget = BudgetManager()
    test_history = TransactionHistoryAnalyzer()

    user_id = uuid.UUID(        "47a74fbc-d4a7-4bce-ab6b-851c0420592d")

    # Dodawanie przykładowych danych
    test_budget.add_expense(user_id, 100.50, "2025-02-20", "Zakupy spożywcze", "Jedzenie")
    test_budget.add_income(user_id, 2000.00, "2025-02-21", "Pensja miesięczna", "Praca")

    expenses = test_history.get_all_user_expenses(user_id)
    incomes = test_history.get_all_user_incomes(user_id)
    operations = test_history.get_user_transactions(user_id)
    date_expenses = test_history.get_user_expenses_by_date(user_id, "2025-02-01", "2025-02-28")

    print("\nWydatki:", expenses)
    print("\nPrzychody:", incomes)
    print("\nWszystkie operacje:", operations)
    print("\nWydatki z zakresu dat:", date_expenses)