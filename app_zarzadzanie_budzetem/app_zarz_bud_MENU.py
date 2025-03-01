def menu():
    #lista_akcji = ListaZakupow()

    while True:
        print("\nMenu: \n"
              "1. Dodanie przychodów do budżetu\n"
              "2. Dodaj wydatki do budżetu\n"
              "3. Dodaj stałe wydatki lub dochody\n"
              "4. Export raportu di pliku\n"
              "5. Przeliczenie Walut\n"
              "6. Historia Wydatków\n"
              "7. Zaplanuj budżet\n"
              "0. Wyjście z Aplikacji")
        choice = input("Wybierz opcję: ")


        if choice == "1":
            print("tu trzeba zrobić kod do dodawania budżetu do użytkownika")
        elif choice == "2":
            print("tu trzeba zrobić kod do odejmowania wydatków od budżetu użytkownika")
        elif choice == "3":
            print("Tu trzeba zrobić funkcję która będzie cyklicznie odejmować wydatki od budżetu użytkownika ")
        elif choice == "4":
            print("Tu trzeba zrobić funkcje exportowania do pliku raportu z budżetem ")
        elif choice == "5":
            print("Tu trzeba zrobić funkcję do przeliczania walut")
        elif choice == "6":
            print("Tu trzeba zrobić funkcję do zapisywania historii wydatków")
        elif choice == "0":
            print("Koniec planowanie/wydawania/zarządzania \n"
                  "***Do ZoBaCzEnIA***")
            break
        else:
            print("BŁĄD.... Spróbuj ponownie....")

if __name__ == "__main__":
    menu()