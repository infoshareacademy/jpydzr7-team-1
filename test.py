import pandas as pd

# Przykładowe dane
data = {
    'Imię': ['Jan', 'Anna', 'Piotr'],
    'Wiek': [28, 34, 22],
    'Miasto': ['Warszawa', 'Kraków', 'Gdańsk']
}

# Tworzymy DataFrame
df = pd.DataFrame(data)

# Zapisujemy do pliku Excel
df.to_excel('tabela.xlsx', index=False)