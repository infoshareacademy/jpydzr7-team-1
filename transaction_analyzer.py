import pandas as pd
import uuid
import os


class TransactionHistoryAnalyzer:
    """
    This class provides functionalities to initialize transaction data, load
    existing records, and filter transactions based on user ID, type of
    transaction (income or expense), and date ranges.
    The transaction data
    is stored in an Excel file and can be retrieved or manipulated
    as needed.
    """
    USER_ID_COLUMN = 'ID_urzytkownika'
    INCOME_COLUMN = 'Przychod'
    EXPENSE_COLUMN = 'Wydatek'
    DATE_COLUMN = 'Data'
    DEFAULT_COLUMNS = ['ID', USER_ID_COLUMN, DATE_COLUMN, INCOME_COLUMN, EXPENSE_COLUMN, 'Opis', 'Kategoria']

    def __init__(self, data_file_path="data.xlsx"):
        self.data_file_path = data_file_path
        if not os.path.exists(data_file_path):
            self._initialize_excel_file()

    def _initialize_excel_file(self):
        """Initializes the Excel file with default columns if it doesn't exist."""
        df = pd.DataFrame(columns=self.DEFAULT_COLUMNS)
        df.to_excel(self.data_file_path, index=False)

    def _load_data(self, convert_dates=False):
        """Loads the data from the Excel file and converts date columns if needed."""
        df = pd.read_excel(self.data_file_path)
        if convert_dates:
            df[self.DATE_COLUMN] = pd.to_datetime(df[self.DATE_COLUMN], format="%d-%m-%Y")
        return df

    def _convert_date_range(self, start_date: str, end_date: str):
        """Converts strings to pandas datetime objects for date comparison."""
        return pd.to_datetime(start_date, dayfirst=True), pd.to_datetime(end_date, dayfirst=True)

    def _filter_transactions(self, data, user_id: uuid.UUID, column_filter=None, start_date=None, end_date=None):
        """Filters transactions by user, type (income/expenses), and optionally by date."""
        user_transactions = data[data[self.USER_ID_COLUMN] == str(user_id)]
        if column_filter:
            user_transactions = user_transactions[user_transactions[column_filter] > 0]
        if start_date and end_date:
            user_transactions = user_transactions[
                (user_transactions[self.DATE_COLUMN] >= start_date) &
                (user_transactions[self.DATE_COLUMN] <= end_date)
                ]
        return user_transactions.to_dict('records')

    def get_all_user_expenses(self, user_id: uuid.UUID):
        """Gets all expenses for the specified user."""
        df = self._load_data()
        return self._filter_transactions(df, user_id, column_filter=self.EXPENSE_COLUMN)

    def get_all_user_incomes(self, user_id: uuid.UUID):
        """Gets all incomes for the specified user."""
        df = self._load_data()
        return self._filter_transactions(df, user_id, column_filter=self.INCOME_COLUMN)

    def get_user_expenses_by_date(self, user_id: uuid.UUID, start_date: str, end_date: str):
        """Gets expenses for the specified user within a date range."""
        df = self._load_data(convert_dates=True)
        start_date, end_date = self._convert_date_range(start_date, end_date)
        return self._filter_transactions(df, user_id, column_filter=self.EXPENSE_COLUMN, start_date=start_date,
                                         end_date=end_date)

    def get_user_incomes_by_date(self, user_id: uuid.UUID, start_date: str, end_date: str):
        """Gets incomes for the specified user within a date range."""
        df = self._load_data(convert_dates=True)
        start_date, end_date = self._convert_date_range(start_date, end_date)
        return self._filter_transactions(df, user_id, column_filter=self.INCOME_COLUMN, start_date=start_date,
                                         end_date=end_date)

    def get_user_transactions(self, user_id: uuid.UUID) -> list[dict]:
        """Gets all transactions for the specified user."""
        df = self._load_data()
        return self._filter_transactions(df, user_id)


if __name__ == "__main__":
    # TEST DATA
    test_budget = TransactionHistoryAnalyzer()
    #user_id = uuid.uuid4()
    user_id = uuid.UUID("47a74fbc-d4a7-4bce-ab6b-851c0420592d")

    # Pobieranie danych
    expenses = test_budget.get_all_user_expenses(user_id)
    incomes = test_budget.get_all_user_incomes(user_id)
    operations = test_budget.get_user_transactions(user_id)
    date_expenses = test_budget.get_user_expenses_by_date(user_id, "01-02-2025", "28-02-2025")

    print("\nWydatki:", expenses)
    print("\nPrzychody:", incomes)
    print("\nWszystkie operacje:", operations)
    print("\nWydatki z zakresu dat:", date_expenses)