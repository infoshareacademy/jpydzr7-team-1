import pandas as pd
import uuid
from datetime import datetime
import os
from transaction_analyzer import TransactionHistoryAnalyzer
import budget_input

class BudgetManager:
    """
    Manages budget operations such as income and expense recordings.

    This class provides functionality to manage personal budgeting by allowing
    users to record income and expenses. Data is stored in an Excel file which
    is initialized and maintained by the class. Each record includes details
    like user ID, date, description, category, and transaction amount.
    """
    USER_ID_COLUMN = 'ID_urzytkownika'
    INCOME_COLUMN = 'Przychod'
    EXPENSE_COLUMN = 'Wydatek'
    DATE_COLUMN = 'Data'
    DEFAULT_COLUMNS = ['ID', USER_ID_COLUMN, DATE_COLUMN, INCOME_COLUMN, EXPENSE_COLUMN, 'Opis', 'Kategoria',"Typ"]

    def __init__(self, file_path="data.xlsx"):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self._initialize_excel_file()


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
        new_data = pd.DataFrame([data], columns=self.DEFAULT_COLUMNS)
        for col in df.columns:
            if col in new_data.columns:
                new_data[col] = new_data[col].astype(df[col].dtype)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(self.file_path, index=False)

    def add_expense(self, user_id: uuid.UUID, amount: float, date: str = None,
                    description: str = None, category: str = None, frequency: str = None):
        """
        Adds an expense record for the given user to the system.
        This method accepts details of an expense, including the user ID, the monetary
        amount, and optionally the date, description, and category, and records it
        to the system. If the date is not provided, the current date will be used.
        The expense data is saved into an Excel file for further record-keeping.
        """
        if not isinstance(user_id, uuid.UUID):
            raise ValueError("ID_urzytkownika musi być typu UUID")
        if amount <= 0:
            raise ValueError("Kwota wydatku musi być większa od 0")

        current_date = date if date else datetime.now().strftime("%d-%m-%Y")

        expense_data = {
            'ID': self._get_next_id(),
            self.USER_ID_COLUMN: str(user_id),
            self.DATE_COLUMN: current_date,
            self.INCOME_COLUMN: 0.0,
            self.EXPENSE_COLUMN: amount,
            'Opis': description if description else '',
            'Kategoria': category if category else '',
            'Typ': frequency if frequency else ''
        }

        self._save_to_excel(expense_data)
        return expense_data

    def add_income(self, user_id: uuid.UUID, amount: float, date: str = None,
                    description: str = None, category: str = None, frequency: str = None):
        """
        Adds an income record to the Excel for a specified user. The income record
        contains details such as user ID, amount, optional description, category,
        and the date of the income. In case the date is not provided, the system
        uses the current date. This method validates that the user ID is of type
        UUID and that the amount is greater than zero. The income record is stored
        in an Excel file via the `_save_to_excel` method.
        """
        if not isinstance(user_id, uuid.UUID):
            raise ValueError("ID_urzytkownika musi być typu UUID!")
        if amount <= 0:
            raise ValueError("Kwota przychodu musi być większa od 0 zł!")

        current_date = date if date else datetime.now().strftime("%d-%m-%Y")

        income_data = {
            'ID': self._get_next_id(),
            self.USER_ID_COLUMN: str(user_id),
            self.DATE_COLUMN: current_date,
            self.INCOME_COLUMN: amount,
            self.EXPENSE_COLUMN: 0.0,
            'Opis': description if description else '',
            'Kategoria': category if category else '',
            'Typ': frequency if frequency else ''
        }

        self._save_to_excel(income_data)
        return income_data


if __name__ == "__main__":
    # TEST DATA
    # Tworzenie instancji testowego budżetu i historii
    test_budget = BudgetManager()
    test_history = TransactionHistoryAnalyzer()

    # Tworzenie testowego UUID usera
    user_id = uuid.UUID("47a74fbc-d4a7-4bce-ab6b-851c0420592d")

    # Dodawanie przykładowych danych (odkomentuj aby dodać te dane do testowego excela):
    # test_budget.add_expense(user_id, 100.50, "20-02-2025", "Zakupy spożywcze", "Jedzenie")
    # test_budget.add_income(user_id, 2000.00, "21-02-2025", "Pensja miesięczna", "Praca")

    expenses = test_history.get_all_user_expenses(user_id)
    incomes = test_history.get_all_user_incomes(user_id)
    operations = test_history.get_user_transactions(user_id)
    date_expenses = test_history.get_user_expenses_by_date(user_id, "01-02-2025", "28-02-2025")

    print("\nWydatki:", expenses)
    print("\nPrzychody:", incomes)
    print("\nWszystkie operacje:", operations)
    print("\nWydatki z zakresu dat:", date_expenses)