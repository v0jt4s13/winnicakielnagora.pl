# Zapis do wina.json/wydarzenia.json wymaga sprawdzenia wersji

Panel zapisuje **cały plik** na raz — `zapisz(dane)` w `cennik.py`/`wydarzenia.py` nigdy
nie sprawdzał, czy plik zmienił się od czasu, gdy caller go wczytał. Dwoje redaktorów
edytujących równocześnie po cichu nadpisywało sobie zmiany (wypadek 2026-09-11).

Każdy nowy sposób zapisu tych dwóch plików **musi** iść przez `zapisz_bezpiecznie()`,
nie przez `zapisz()` bezpośrednio (poza testami, które celowo dokumentują surowe
zachowanie `zapisz()` — patrz niżej).

## Kontrakt

```python
# cennik.py / wydarzenia.py (bliźniacze funkcje w obu)
wersja_pliku() -> str                     # skrót tresci pliku na dysku
podsumuj_roznice(stare, nowe) -> list[str]  # krotki opis zmian, liczony po polu id
zapisz_bezpiecznie(dane, bazowa_wersja, bazowe_dane=None) -> str  # zwraca nowa wersje
# rzuca KonfliktZapisu(aktualna_wersja, roznice), gdy bazowa_wersja != wersja_pliku()
```

Kształt żądania/odpowiedzi HTTP (`wsgi.py` i `tools/panel/serwer.py`, oba endpointy
`zapisz`/`wydarzenia-zapisz`):

```json
// POST body
{ "wersja": "<hash z ostatniego wczytania>", "bazowe_dane": {...}, "dane": {...} }
// odpowiedz sukcesu
{ "ok": true, "wersja": "<nowy hash>", ... }
// odpowiedz konfliktu — 409, plik NIE zostal dotkniety
{ "ok": false, "konflikt": true, "komunikat": "...", "roznice": ["Nazwa: zmienione pole(a) ..."] }
```

`panel.js` trzyma migawkę sprzed edycji (`cennikBazowy`/`wydarzeniaBazowe`, zamrożoną
przez `JSON.parse(JSON.stringify(...))` przy każdym wczytaniu i udanym zapisie) obok
mutowanego w miejscu `cennik`/`wydarzenia` — bez tej migawki serwer nie ma z czym
policzyć `roznice` przy konflikcie.

## Exceptions

- `zapisz()` (bez `_bezpiecznie`) zostaje nietknięta i nadal robi „ostatni zapis
  wygrywa" — `tools/test-wydarzenia.py` explicite to sprawdza jako udokumentowane
  zachowanie surowej funkcji. Nie zmieniaj tego testu.
- `bazowe_dane` jest opcjonalne — brak (np. wywołanie spoza panelu) daje pustą listę
  `roznice`, ale konflikt nadal blokuje zapis.

## Ograniczenie (świadome)

To wykrywanie konfliktu, **nie scalanie**. Odrzucony zapis wymaga, żeby człowiek kliknął
„Odrzuć zmiany" i wprowadził swoją zmianę ponownie na świeżych danych. Miękka blokada
„ktoś inny to teraz edytuje" (ostrzeżenie przy otwarciu pozycji) jest celowo poza
zakresem — wymagałaby osobnego stanu (plik blokady z TTL) i nie naprawia samego
wypadku, bo to kontrola wersji zapobiega utracie danych, nie blokada.

## Why

Panel nie ma bazy danych ani tożsamości redaktorów (jedno wspólne hasło Basic Auth) —
porównanie skrótu pliku na dysku jest najprostszym odpornym zamiennikiem prawdziwego
wersjonowania dokumentu, bez dokładania zależności do statycznego projektu.
