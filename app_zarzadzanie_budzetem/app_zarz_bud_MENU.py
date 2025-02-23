def menu():
    #lista_akcji = ListaZakupow()

    while True:
        print("\nMenu: \n"
              "1. Dodanie przychodów do budżetu\n"
              "2. Odejmowanie wydatków od budżetu\n"
              "3. Dodanie stałych/cyklicznych wydatków\n"
              "4. Export raportu di pliku\n"
              "5. Przeliczenie Walut\n"
              "6. Historia Wydatków\n"
              "0. Wyjście z Aplikacji")
        wybor = input("Wybierz opcję: ")


        if wybor == "1":
            #TODO
            print("tu trzeba zrobić kod do dodawania budzetu do użytkownika")
        elif wybor == "2":
            print("tu trzeba zrobić kod do odejmowania wydatków od budżetu użytkownika")
        elif wybor == "3":
            print("Tu trzeba zrobić funkcję która będzie cyklicznie odejmować wydatki od budżetu użytkownika ")
        elif wybor == "4":
            print("Tu trzeba zrobić funkcje exportowania do pliku raportu z budżetem ")
        elif wybor == "5":
            print("Tu trzeba zrobić funkcję do przeliczania walut")
        elif wybor == "6":
            print("Tu trzeba zrobić funkcję do zapisywania historii wydatków")
        elif wybor == "0":
            print("Koniec planowanie/wydawania/zarządzania \n"
                  "***Do ZoBaCzEnIA***")
            break
        else:
            print("BŁĄD.... Spróbuj ponownie....")

if __name__ == "__main__":
    menu()