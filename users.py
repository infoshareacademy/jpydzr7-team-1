import uuid
import pandas as pd
import os
import hashlib
import random
import string
import re

class Family:
    def __init__(self, family_name: str):
        self.family_name = family_name
        self.family_id = str(uuid.uuid4()).split('-')[0]
        print(f"Tworzona rodzina: {self.family_name}, ID: {self.family_id}")

    def to_dict(self) -> dict:
        return {
            "family_id": self.family_id,
            "family_name": self.family_name
        }

    @staticmethod
    def save_family_to_excel(family):
        family_dict = family.to_dict()
        df = pd.DataFrame([family_dict])

        file_path = 'dane_uzytkownikow.xlsx'
        print(f"Zapisuję rodzinę do pliku: {file_path}")

        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as xls:
                if 'Families' in xls.sheet_names:
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, index=False, sheet_name='Families', header=False,
                                    startrow=len(xls.parse('Families')) + 1)
                else:
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, index=False, sheet_name='Families', header=True)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, index=False, sheet_name='Families', header=True)


    @staticmethod
    def create_family():
        family_name = input("Podaj nazwę rodziny, którą chcesz utworzyć: ")
        new_family = Family(family_name)
        Family.save_family_to_excel(new_family)

    @staticmethod
    def validate_family_id_exists(family_id: str) -> bool:
        """Sprawdza, czy family_id istnieje w pliku families.xlsx"""
        file_path = 'dane_uzytkownikow.xlsx'
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name='Families')
            # Sprawdzamy, czy family_id znajduje się wśród family_id w pliku rodzin
            return family_id in df['family_id'].values
        return False


class User:
    def __init__(self,user_id, name, surname, email, login, password, family_id, parent_id=None):
        self.user_id = user_id
        self.name = name
        self.surname = surname
        self.email = email
        self.login = login
        self.password = password
        self.family_id = family_id
        self.parent_id = parent_id


    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "login": self.login,
            "password": self.password,
            "family_id": self.family_id,
            "parent_id": self.parent_id
            }

    @staticmethod
    def wygenerujHaslo(size, chars=string.ascii_letters + string.digits + string.punctuation):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Sprawdzanie, czy e-mail ma poprawny format."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(email_regex, email))

    @staticmethod
    def save_data_to_excel(in_user):
        user_dict = in_user.to_dict()
        df = pd.DataFrame([user_dict])

        file_path = 'dane_uzytkownikow.xlsx'

        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as xls:
                if 'Users' in xls.sheet_names:
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, index=False, sheet_name='Users', header=False, startrow=len(xls.parse('Users')) + 1)
                else:
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, index=False, sheet_name='Users', header=True)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, index=False, sheet_name='Users', header=True)

    @staticmethod
    def create_user():

        while True:
            family_id = input("Podaj identyfikator rodziny do której chcesz dołączyć. Jeżeli nie posiadasz jeszcze ID dla swojej rodziny, wciśnij enter: ")

            if Family.validate_family_id_exists(family_id):
                print(f"Rodzina z ID {family_id} istnieje.")
                break
            if not family_id:
                family = Family.create_family()
                family_id = input("Aby kontynuować logowanie, wpisz identyfikator rodziny(ID): ")
                break
            else:
                print(f"Rodzina z ID {family_id} nie istnieje. Spróbuj ponownie.")

        user_id = str(uuid.uuid4()).split('-')[0]
        name = input("Podaj imię: ")
        surname = input("Podaj nazwisko: ")

        while True:
            email = input("Podaj adres e-mail (obowiązkowy): ")
            if email == "":
                print("Email jest wymagany. Proszę podać email.")
                continue
            elif not User.validate_email(email):
                print("Nieprawidłowy format e-maila. Proszę podać poprawny adres e-mail.")
                continue
            else:
                break
        login = input("Podaj login. Jeżeli pole pozostanie puste, twój E-mail zostanie automatycznie przypisany jako login. Login:: ")
        if not login:
            login = email
        password_user = input("Podaj haslo: ")
        if not password_user:
            print("Nie podano hasła. Hasło zostanie wygenerowane automatycznie")
            while True:
                try:
                    haslo_generowane = int(input("Podaj długosc hasła: "))
                    if haslo_generowane > 0:
                        break
                    else:
                        print(
                            "Długość hasła musi byc liczbą większą od 0. Zalecana długość hasła to minimum 8 znaków. Spróbuj ponownie")
                except ValueError:
                    print("Wybrana długość hasła musi byc liczbą. Spróbuj ponownie.")
            print("Twoje nowe hasło to: ")
            password_user = User.wygenerujHaslo(haslo_generowane)
            print(password_user)
        h = hashlib.new('SHA256')
        h.update(password_user.encode())
        password = h.hexdigest()
        new_user = User(user_id, name, surname, email, login, password, family_id)
        User.save_data_to_excel(new_user)
        print("Dane użytkownika zostały pomyślnie zapisane.")

    @staticmethod
    def get_user_by_login(login):
        file_path = 'dane_uzytkownikow.xlsx'

        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as xls:
                if 'Users' in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name='Users')

                    df['login'] = df['login'].str.strip().str.lower()

                    login = login.strip().lower()

                    user_data = df[df['login'] == login]

                    if not user_data.empty:
                        return user_data.iloc[0]
                    else:
                        print("Nie znaleziono użytkownika o podanym loginie.")
                        return None
                else:
                    print("Brak arkusza 'Users' w pliku.")
                    return None
        else:
            print("Plik 'dane_uzytkownikow.xlsx' nie istnieje.")
            return None



    @staticmethod
    def display_user_data():
        login = input("Podaj login użytkownika: ")
        user_data = User.get_user_by_login(login)

        if user_data is not None:
            user_data_dict = user_data.to_dict()

            user_data_dict.pop('password', None)
            print("Dane użytkownika:")
            for key, value in user_data_dict.items():
                print(f"{key}: {value}")
        else:
            print("Nie znaleziono użytkownika o podanym loginie.")

    @staticmethod
    def remove_user_by_login_and_password(login, password):
        file_path = 'dane_uzytkownikow.xlsx'

        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as xls:
                if 'Users' in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name='Users')

                    user_to_remove = df[df['login'] == login]

                    if not user_to_remove.empty:

                        if user_to_remove['password'].iloc[0] == password:

                            df = df[df['login'] != login]

                            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                                df.to_excel(writer, index=False, sheet_name='Users', header=True)
                            print(f"Użytkownik o loginie {login} został usunięty.")
                        else:
                            print("Nieprawidłowe hasło.")
                    else:
                        print("Nie znaleziono użytkownika o podanym loginie.")
                else:
                    print("Brak arkusza 'Users' w pliku.")
        else:
            print("Plik 'dane_uzytkownikow.xlsx' nie istnieje.")


    def delete_user():
        login_to_remove = input("Podaj login użytkownika, którego chcesz usunąć: ")
        password_to_remove_user = input("Podaj hasło użytkownika, którego chcesz usunąć: ")
        h = hashlib.new('SHA256')
        h.update( password_to_remove_user.encode())
        password_to_remove = h.hexdigest()
        User.remove_user_by_login_and_password(login_to_remove, password_to_remove)

    @staticmethod
    def validate_parent_id_as_user_id(parent_id: str) -> bool:
        """Sprawdza, czy parent_id istnieje w pliku użytkowników jako user_id"""
        file_path = 'dane_uzytkownikow.xlsx'
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name='Users')
            return parent_id in df['user_id'].values
        return False


class Kid(User):
    def __init__(self,user_id, name, surname, email, login, password, family_id, parent_id):
     super().__init__(user_id, name, surname, email, login, password, family_id)
     self.parent_id = parent_id

    @staticmethod
    def create_kid():
        user_id = str(uuid.uuid4()).split('-')[0]
        while True:
            family_id = input( "Podaj identyfikator rodziny do której chcesz dołączyć. ")

            if Family.validate_family_id_exists(family_id):
                print(f"Rodzina z ID {family_id} istnieje.")
                break
            else:
                print(f"Rodzina z ID {family_id} nie istnieje. Spróbuj ponownie.")
        name = input("Podaj imię: ")
        surname = input("Podaj nazwisko: ")
        while True:
            email = input("Podaj adres e-mail (obowiązkowy): ")
            if email == "":
                print("Email jest wymagany. Proszę podać email.")
                continue
            elif not User.validate_email(email):
                print("Nieprawidłowy format e-maila. Proszę podać poprawny adres e-mail.")
                continue
            else:
                break
        login = input("Podaj login. Jeżeli pole pozostanie puste, twój E-mail zostanie automatycznie przypisany jako login. Login: ")
        if not login:
            login = email
        password_user = input("Podaj haslo: ")
        if not password_user:
            print("Nie podano hasła. Hasło zostanie wygenerowane automatycznie")
            while True:
                try:
                    haslo_generowane = int(input("Podaj długosc hasła: "))
                    if haslo_generowane > 0:
                        break
                    else:
                        print( "Długość hasła musi byc liczbą większą od 0. Zalecana długość hasła to minimum 8 znaków. Spróbuj ponownie")
                except ValueError:
                    print("Wybrana długość hasła musi byc liczbą. Spróbuj ponownie.")
            print("Twoje nowe hasło to: ")
            password_user = Kid.wygenerujHaslo(haslo_generowane)
            print(password_user)
        h = hashlib.new('SHA256')
        h.update(password_user.encode())
        password = h.hexdigest()
        while True:
            parent_id = input("Podaj parent_id (user_ID rodzica): ")
            if parent_id == "":
                print("parent_id jest wymagane. Proszę podać parent_id.")
                continue
            elif not User.validate_parent_id_as_user_id(parent_id):
                print(f"Użytkownik z parent_id {parent_id} nie istnieje. Spróbuj ponownie ")
                return
            else:
                break

        new_kid = Kid(user_id, name, surname, email, login, password, family_id, parent_id)

        User.save_data_to_excel(new_kid)
        print("Dane użytkownika zostały pomyślnie zapisane.")

# Polecenia do TESTOW:

# Wprowadzanie danych nowego uzytkownika:

status = input("Wybierz swoj status (1 = rodzic / 2 = dziecko): ")
if status == "1":
    User.create_user()
elif status == "2":
    Kid.create_kid()
else:
    print("Bledna odpowiedz. Proszę wybierz '1' lub '2'.")

# Wywietlanie danych uzytkownika

# display_option = input("Czy chcesz wyświetlić dane użytkownika? (tak/nie): ")
# if display_option.lower() == "tak":
#     User.display_user_data()


 # Usuwanie użytkownika

# delete_option = input("Czy chcesz usunąć użytkownika? (tak/nie): ")
# if delete_option.lower() == "tak":
#     User.delete_user()

# Tworzenie nowej rodziny

# Family.create_family()