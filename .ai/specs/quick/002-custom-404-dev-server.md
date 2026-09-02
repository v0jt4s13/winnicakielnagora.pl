# Projektowa strona 404 w podglądzie lokalnym

## Zakres

- Zastąpić standardową odpowiedź 404 modułu `http.server` zawartością `404.html`.
- Zachować prawidłowy kod HTTP 404 dla nieznanych adresów.
- Nie dodawać zależności ani nie zmieniać produkcyjnego routingu Flask.

## Miejsce zmiany

- `tools/dev-server.py` — lokalny serwer oparty wyłącznie na bibliotece standardowej.
- `AGENTS.md` — aktualne polecenie uruchomienia podglądu.

## Powód

`python3 -m http.server` generuje własny komunikat „Error response” i nie korzysta z
projektowego pliku `404.html`, przez co zaprojektowany ekran nie jest widoczny lokalnie.

## Weryfikacja

- Istniejący plik zwraca kod 200.
- Nieznany adres zwraca kod 404 i treść z `404.html`.
- Obraz, CSS oraz JavaScript strony 404 są dostępne.
