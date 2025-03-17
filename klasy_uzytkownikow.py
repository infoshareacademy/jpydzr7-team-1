import uuid
import pandas as pd
import os

class Family:
    def __init__(self, family_name: str):
        self.family_name = family_name
        self.uuid = uuid.uuid4()

class User:
    def __init__(self,user_id, name, surname, email, login, password, family_id):
        self.user_id = user_id
        self.name = name
        self.surname = surname
        self.email = email
        self.login = login
        self.password = password
        self.family_id = family_id


    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "login": self.login,
            "password": self.password,
            "family_id": self.family_id
            }


    @staticmethod
    def save_data_to_excel(in_user):
        user_dict = in_user.to_dict()

        df = pd.DataFrame([user_dict])

        try:
            with pd.ExcelWriter('data.xlsx', engine='openpyxl', mode='a') as writer:
                df.to_excel(writer, index=False, sheet_name='Users', header=not writer.sheets)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu do Excel: {e}")


    @staticmethod
    def create_user():
        user_id = str(uuid.uuid4())
        name = input("Podaj imię: ")
        surname = input("Podaj nazwisko: ")
        email = input("Podaj E-mail: ")
        login = input("Podaj login. Jeżeli pole pozostanie puste, twój E-mail zostanie automatycznie przypisany jako login. Login:: ")
        password = input("Podaj haslo: ")
        family_id = input("Podaj identyfikator swojej rodziny: ")

        new_user = User(user_id, name, surname, email, login, password, family_id)
        User.save_data_to_excel(new_user)
        print("Dane użytkownika zostały pomyślnie zapisane.")


class Kid(User):
    def __init__(self,user_id, name, surname, email, login, password, family_id, parent_id):
     super().__init__(user_id, name, surname, email, login, password, family_id)
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
    def create_kid():
        user_id = str(uuid.uuid4())
        name = input("Podaj imię: ")
        surname = input("Podaj nazwisko: ")
        email = input("Podaj E-mail: ")
        login = input("Podaj login. Jeżeli pole pozostanie puste, twój E-mail zostanie automatycznie przypisany jako login. Login:: ")
        password = input("Podaj haslo: ")
        family_id = input("Podaj identyfikator swojej rodziny: ")
        parent_id = input("Enter parent ID: ")

        new_kid = Kid(user_id, name, surname, email, login, password, family_id, parent_id)

        User.save_data_to_excel(new_kid)
        print("Dane użytkownika zostały pomyślnie zapisane.")


status = input("Wybierz swoj status (1 = rodzic / 2 = dziecko): ")
if status == "1":
    User.create_user()
elif status == "2":
    Kid.create_kid()
else:
    print("Bledna odpowiedz. Proszę wybierz '1' lub '2'.")