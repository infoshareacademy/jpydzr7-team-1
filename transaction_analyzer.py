import pandas as pd
import uuid
import os


class TransactionHistoryAnalyzer:
    USER_ID_COLUMN = 'ID_urzytkownika'
    INCOME_COLUMN = 'Przychod'
    DATE_COLUMN = 'Data'
    DEFAULT_COLUMNS = ['ID', USER_ID_COLUMN, DATE_COLUMN, INCOME_COLUMN, 'Wydatek', 'Opis', 'Kategoria']

    def __init__(self, data_file_path="data.xlsx"):
        self.data_file_path = data_file_path
        if not os.path.exists(data_file_path):
            self._initialize_excel_file()

    def _initialize_excel_file(self):
        df = pd.DataFrame(columns=self.DEFAULT_COLUMNS)
        df.to_excel(self.data_file_path, index=False)


    def _load_data(self, convert_dates=False):
        """Metoda pomocnicza do wczytywania danych z pliku Excel"""
        df = pd.read_excel(self.data_file_path)
        if convert_dates:
            df['Data'] = pd.to_datetime(df['Data'])
        return df

    def _convert_date_range(self, start_date: str, end_date: str):
        """Metoda pomocnicza do konwersji zakresu dat"""
        return pd.to_datetime(start_date), pd.to_datetime(end_date)

    def _filter_incomes_by_date(self, data, user_id: uuid.UUID, start_date: str, end_date: str):
        """
        Filters the data for incomes for a specific user and date range.
        """
        return data[
            (data[self.USER_ID_COLUMN] == str(user_id)) &
            (data[self.INCOME_COLUMN] > 0) &
            (data[self.DATE_COLUMN] >= start_date) &
            (data[self.DATE_COLUMN] <= end_date)
            ].to_dict('records')

    def get_all_user_expenses(self, user_id: uuid.UUID):
        """Zwracanie wszystkich wydatków użytkownika"""
        df = self._load_data()
        return df[(df[self.USER_ID_COLUMN] == str(user_id)) & (df['Wydatek'] > 0)].to_dict('records')

    def get_all_user_incomes(self, user_id: uuid.UUID):
        """Zwracanie wszystkich przychodów użytkownika"""
        df = self._load_data()
        return df[(df[self.USER_ID_COLUMN] == str(user_id)) & (df['Przychod'] > 0)].to_dict('records')

    def get_user_expenses_by_date(self, user_id: uuid.UUID, start_date: str, end_date: str):
        """Zwracanie wydatków użytkownika z zakresu dat"""
        df = self._load_data(convert_dates=True)
        start_date, end_date = self._convert_date_range(start_date, end_date)

        return df[(df[self.USER_ID_COLUMN] == str(user_id)) &
                  (df['Wydatek'] > 0) &
                  (df['Data'] >= start_date) &
                  (df['Data'] <= end_date)].to_dict('records')

    def get_user_incomes_by_date(self, user_id: uuid.UUID, start_date: str, end_date: str):
        """
        Fetches and returns a list of income records for a specific user within
        a given date range. This function filters the data based on the specified
        user ID, start date, and end date. It also ensures that only records with
        positive income values are returned.

        :param user_id: The unique identifier of the user for whom the income
            records are being retrieved.
        :type user_id: uuid.UUID
        :param start_date: The start date of the date range for filtering
            the income records, formatted as a string.
        :type start_date: str
        :param end_date: The end date of the date range for filtering
            the income records, formatted as a string.
        :type end_date: str
        :return: A list of dictionaries representing the income records
            that match the specified criteria. Each dictionary contains the
            data for an individual record.
        :rtype: list[dict]
        """
        df = self._load_data(convert_dates=True)
        start_date, end_date = self._convert_date_range(start_date, end_date)

        return df[(df[self.USER_ID_COLUMN] == str(user_id)) &
                  (df['Przychod'] > 0) &
                  (df['Data'] >= start_date) &
                  (df['Data'] <= end_date)].to_dict('records')

    def get_user_transactions(self, user_id: uuid.UUID) -> list[dict]:
        """
        Retrieve all user transactions (incomes and expenses).
            Args: The unique identifier of the user.
            Returns: A list of all transactions for the specified user.
        """

        data_frame = self._load_data()
        user_transactions_filter = data_frame[self.USER_ID_COLUMN] == str(user_id)
        return data_frame[user_transactions_filter].to_dict('records')


if __name__ == "__main__":
    # TEST DATA
    budget = TransactionHistoryAnalyzer()
    #user_id = uuid.uuid4()
    user_id = uuid.UUID("47a74fbc-d4a7-4bce-ab6b-851c0420592d")

    # Pobieranie danych
    expenses = budget.get_all_user_expenses(user_id)
    incomes = budget.get_all_user_incomes(user_id)
    operations = budget.get_user_transactions(user_id)
    date_expenses = budget.get_user_expenses_by_date(user_id, "2025-02-01", "2025-02-28")

    print("Wydatki:", expenses)
    print("Przychody:", incomes)
    print("Wszystkie operacje:", operations)
    print("Wydatki z zakresu dat:", date_expenses)