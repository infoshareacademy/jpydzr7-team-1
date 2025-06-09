
## Konfiguracja zmiennych środowiskowych (.env)

### Instalacja

Pakiet `python-dotenv` jest już zainstalowany w projekcie (sprawdź `requirements.txt`).

### Konfiguracja

1. **Utwórz plik `.env` w głównym katalogu projektu** (na tym samym poziomie co `manage.py`):
```
bash touch .env
``` 

2. **Dodaj zmienne środowiskowe do pliku `.env`**:
```
DB_USER=twoja_nazwa_uzytkownika
DB_PASSWORD=twoje_haslo_do_bazy
``` 
Przykładowy plik [.env.example](Budget_Project/.env.example)

### Jak używać zmiennych z .env

W pliku `settings.py` zmienne są już skonfigurowane i ładowane automatycznie:
python from dotenv import load_dotenv import os


### Przykłady użycia

- `os.getenv('NAZWA_ZMIENNEJ', 'domyślna')` - zwraca wartość zmiennej lub domyślną wartość

### Dobre praktyki

1. **Nigdy nie commituj swojego pliku `.env`** do repozytorium
2. **Zawsze ustaw domyślne wartości** dla zmiennych opcjonalnych
3. **Dokumentuj wszystkie wymagane zmienne środowiskowe** w README

### Rozwiązywanie problemów

- Jeśli zmienne nie są ładowane, sprawdź czy plik `.env` znajduje się w odpowiednim katalogu
- Upewnij się, że nie ma spacji wokół znaku `=` w pliku `.env`
- Sprawdź czy `load_dotenv()` jest wywołane przed użyciem `os.getenv()`
