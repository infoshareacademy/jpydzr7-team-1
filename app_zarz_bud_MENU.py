import uuid
from email.policy import default

import budget_input

user_ID = uuid.UUID("47a74fbc-d4a7-4bce-ab6b-851c0420592d")

def menu():
    #lista_akcji = ListaZakupow()

    while True:
        print("\nMenu: \n"
              "1. Dodanie przychodów do budżetu\n"
              "2. Dodaj wydatki do budżetu\n"
              # "3. Dodaj stałe wydatki lub dochody\n"
              "3. Export raportu do pliku\n"
              "4. Przeliczenie Walut\n"
              "5. Historia Wydatków\n"
              "6. Zaplanuj budżet\n"
              "0. Wyjście z Aplikacji")
        choice = input("Wybierz opcję: ")


        if choice == "1":
            budget_input.take_input("income", user_ID)
        elif choice == "2":
            budget_input.take_input("expense", user_ID)
        # elif choice == "3":
        #     print("Tu trzeba zrobić funkcję która będzie cyklicznie odejmować wydatki od budżetu użytkownika ")
        elif choice == "3":
            print("Tu trzeba zrobić funkcje exportowania do pliku raportu z budżetem ")
        elif choice == "4":
            print("Tu trzeba zrobić funkcję do przeliczania walut")
        elif choice == "5":
            print("Tu trzeba zrobić funkcję do zapisywania historii wydatków")
        elif choice == "6":
            print("Koniec planowanie/wydawania/zarządzania \n"
                  "***Do ZoBaCzEnIA***")
            break
        else:
            print("BŁĄD.... Spróbuj ponownie....")

if __name__ == "__main__":
    menu()