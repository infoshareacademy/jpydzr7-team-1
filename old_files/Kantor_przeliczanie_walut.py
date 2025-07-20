import requests


class Kantor:
    #Funkcja wyświetlania walut
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):

        if from_currency == to_currency:
            return amount  # No conversion needed

        url = f"https://api.frankfurter.app/latest"
        params = {
            "amount": amount,
            "from": from_currency,
            "to": to_currency
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error fetching exchange rates: {response.status_code} {response.text}")

        #print(response)
        data = response.json()

        #print(data)

        if "rates" not in data or to_currency not in data["rates"]:
            raise Exception("Currency not found in API response.")

        return data["rates"][to_currency]



    #funkcja wyświtlania obsługiwanych walut
    @staticmethod
    def get_supported_currencies():

        url = "https://api.frankfurter.app/currencies"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching supported currencies: {response.status_code} {response.text}")

        return response.json()


    #MENU
    @staticmethod
    def menu():
        while True:
            print("\n---Menu KANTOR---")
            print("1. Wyświetl obsługiwane waluty")
            print("2. Przelicz walutę")
            print("3. Wyjdź")

            choice = input("Wybierz opcję: ")

            if choice == "1":
                try:
                    currencies = Kantor.get_supported_currencies()
                    print("Supported currencies:")
                    for code, name in currencies.items():
                        print(f"{code}: {name}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "2":
                try:
                    amount = float(input("Wpisz kwotę którą chcesz przeliczyć "))
                    from_currency = input("Wpisz w jakiej walucie wprowadziłeś kwotę do przeliczenia (domyślnie PLN): ").strip().upper() or "PLN"
                    to_currency = input("Wpisz na jaką walute chcesz przeliczyć: ").strip().upper()

                    converted_amount = Kantor.convert_currency(amount, from_currency.upper(), to_currency)
                    print(f"{amount} {from_currency.upper()} jest równe {converted_amount:.2f} {to_currency}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == "3":
                print("koniec przeliczania walut")
                break

            else:
                print("Nieprawidłowy wybór, spróbuj ponownie")
if __name__ == "__main__":
    Kantor.menu()
