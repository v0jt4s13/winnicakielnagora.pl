# SPEC-002 — Panel redakcyjny do `data/wina.json`

**Status**: propozycja do akceptacji
**Rozmiar**: M
**Data**: 2026-09-02
**Zależy od**: SPEC-001 (definiuje strukturę `data/wina.json`)

## Overview

`data/wina.json` (SPEC-001) jest jedynym źródłem asortymentu i cen. Plik jest prosty, ale
edytowanie JSON-a w notatniku to praca dla programisty: brakujący przecinek albo cudzysłów
wysypuje cały sklep, a osoba nietechniczna nie ma jak sprawdzić, czy zrobiła to dobrze.

Ta specyfikacja opisuje **lokalny panel redakcyjny** — stronę WWW z formularzem, która czyta
i zapisuje `data/wina.json`, waliduje dane przed zapisem i pokazuje podgląd karty produktu
dokładnie takiej, jaka pojawi się w sklepie.

**Panel nie jest częścią witryny.** Uruchamia się go ręcznie na komputerze Właściciela,
nasłuchuje wyłącznie na `127.0.0.1` i nigdy nie trafia na produkcję.

### Zakres

- `tools/panel/serwer.py` — lokalny serwer HTTP (biblioteka standardowa Pythona, bez Flaska).
- `tools/panel/panel.html` + `panel.js` + `panel.css` — interfejs.
- Odczyt, walidacja i zapis `data/wina.json` z kopią zapasową.
- Podgląd karty produktu i strony odmiany, do której pozycja się odwołuje.

### Poza zakresem

- Uwierzytelnianie, konta, role — panel działa tylko lokalnie i tylko dla osoby przy klawiaturze.
- Edycja treści stron odmian, sekcji `#o-nas`, `#kontakt` i wydarzeń — panel dotyka
  **wyłącznie** `data/wina.json`.
- Wgrywanie zdjęć — panel wybiera spośród plików już leżących w `attached_assets/photos/`.
  Nowe zdjęcia dokłada się przez `tools/optimize-photos.py`.
- Publikacja na serwer — po zapisie Właściciel robi commit i wdrożenie jak dotąd.

## User Stories

### Story 1 — Właściciel podnosi cenę i wycofuje wino (happy path)

**Persona**: Właściciel winnicy. Nie programuje, pracuje na własnym laptopie. Chce podnieść
cenę jednego wina o 5 zł i oznaczyć drugie jako niedostępne, bo się skończyło.

**Krok 1.** Uruchamia panel jednym poleceniem i otwiera adres, który sam się wypisze.

```
$ python3 tools/panel/serwer.py
Panel cennika: http://127.0.0.1:8765
Plik: /home/vs/repo-agents/winnica/data/wina.json  (6 pozycji)
Zatrzymanie: Ctrl+C
```

**Krok 2.** Widzi listę pozycji.

```
┌──────────────────────────────────────────────────────────────┐
│  Cennik — 6 pozycji                        [ + Dodaj wino ]  │
├──────────────────────────────────────────────────────────────┤
│  ▸ Souvignier Gris 2024   Białe    65,00 zł   ● dostępne     │
│  ▸ St. Pepin 2024         Białe    59,00 zł   ● dostępne     │
│  ▸ Monarch 2023           Czerwone 58,50 zł   ● -10%         │
│  ▸ Sok z białych winogron Soki     18,00 zł   ○ niedostępne  │
├──────────────────────────────────────────────────────────────┤
│  ⬤ Niezapisane zmiany            [ Odrzuć ]  [ Zapisz ]      │
└──────────────────────────────────────────────────────────────┘
```

**Krok 3.** Klika pozycję, formularz się rozwija.

```
┌──────────────────────────────────────────────────────────────┐
│  Souvignier Gris                                    [ Usuń ] │
│  Nazwa      [Souvignier Gris          ]                      │
│  Odmiana    [souvignier-gris        ▾]  → wina/souvignier-…  │
│  Kategoria  [Białe                  ▾]                       │
│  Rocznik    [2024]   Alkohol [12.0] %   Pojemność [750] ml   │
│  Cena brutto[  70,00] zł    Rabat [ 0] %                     │
│  ☑ dostępne                                                  │
│  Opis       [Wytrawne wino o aromatach brzoskwini…         ] │
│  Zdjęcie    [souvignier-gris-kiscie-02 ▾]  [ podgląd ]       │
│                                                              │
│  ┌── Tak zobaczy to klient ──────────────────────────────┐   │
│  │  [foto]  Souvignier Gris                              │   │
│  │          Rocznik 2024 • 12.0% alk.                    │   │
│  │          70,00 zł     netto: 56,91 zł      [ Dodaj ]  │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

> **Za kulisami**: podgląd używa **tej samej funkcji** `renderProductCard()` z
> `assets/js/main.js`, co sklep, i tego samego `assets/css/style.css`. Dzięki temu nie może się
> rozjechać z tym, co widzi klient. Netto (56,91 zł) jest wyliczone, nie wpisane.

**Krok 4.** Zmienia cenę na 70,00, przy soku odznacza „dostępne", klika **Zapisz**.

```
✓ Zapisano data/wina.json (6 pozycji)
  Kopia poprzedniej wersji: data/wina.json.bak
  Pamiętaj o commicie i wdrożeniu.
```

> **Za kulisami**: `POST /api/zapisz` z całą treścią pliku. Serwer waliduje strukturę, zapisuje
> starą wersję jako `wina.json.bak`, po czym zapisuje nową **atomowo** (plik tymczasowy
> + `os.replace`), żeby przerwany zapis nie zostawił uszkodzonego JSON-a.

**Zmiana vs. stan obecny**: dziś zmiana ceny to edycja sześciu miejsc w markupie `index.html`
(SPEC-001 to likwiduje), a po SPEC-001 — ręczna edycja JSON-a z ryzykiem literówki. Po tej
zmianie to formularz z podglądem i walidacją.

### Story 2 — Właściciel dodaje sok, czyli nową kategorię (ścieżka alternatywna)

**Persona**: ten sam Właściciel, ale zadanie dotyka struktury, nie tylko wartości: soki
winogronowe to kategoria, której jeszcze nie ma w cenniku.

**Krok 1.** Klika **+ Dodaj wino**. Formularz startuje pusty, `id` proponuje się samo
z nazwy i rocznika (`sok-z-bialych-winogron`), ale można je nadpisać.

**Krok 2.** W polu „Kategoria" wybiera **+ nowa kategoria…** i wpisuje `Soki`.

> **Za kulisami**: nowa wartość dopisuje się do tablicy `kategorie` w tym samym pliku. Filtr
> w sklepie renderuje swoje opcje z tej tablicy (SPEC-001), więc nic w HTML-u nie wymaga zmiany.
> Panel ostrzega: „Kategoria »Soki« pojawi się w filtrze sklepu".

**Krok 3.** Zostawia puste pola „Rocznik" i „Alkohol" — dla soku nie mają sensu.

> **Za kulisami**: oba pola są opcjonalne (SPEC-001). Puste = pominięte w JSON, a karta
> produktu nie pokaże wtedy linijki „Rocznik … • …% alk.".

**Krok 4.** W polu „Odmiana" nie ma pasującej pozycji, bo sok nie pochodzi z jednej odmiany.
Panel **nie pozwala zapisać** bez `odmiana_slug` i tłumaczy dlaczego.

```
⚠ Pozycja musi wskazywać odmianę — z niej bierze się link „zobacz opis"
  na karcie w sklepie. Jeśli sok nie pochodzi z jednej odmiany, utwórz
  najpierw stronę zbiorczą i wybierz ją tutaj.
```

**Zmiana vs. stan obecny**: to jest przypadek, który przy ręcznej edycji JSON-a przeszedłby bez
echa i zostawił w sklepie kartę z martwym linkiem — `wsgi.py` oddaje na nieznany adres stronę
główną ze statusem 200 (`TODO.md` #5), więc nikt by tego nie zauważył. **Otwarta decyzja
do rozstrzygnięcia z Właścicielem**: czy soki dostają własną stronę, czy `odmiana_slug` ma być
opcjonalny dla kategorii innej niż wino. Do czasu decyzji obowiązuje wariant ostrzejszy
(pole wymagane).

### Story 3 — Ktoś próbuje otworzyć panel z innego komputera (przypadek brzegowy)

**Persona**: dowolna osoba w tej samej sieci Wi-Fi, przypadkiem albo celowo.

**Krok 1.** Wpisuje `http://192.168.1.15:8765` (adres laptopa Właściciela w sieci lokalnej).

**Krok 2.** Nie dostaje nic — połączenie jest odrzucane.

> **Za kulisami**: serwer robi `bind` **wyłącznie** na `127.0.0.1`, więc nie odpowiada na innym
> interfejsie. To pierwsza i najważniejsza linia obrony. Druga: każde żądanie zapisu sprawdza,
> czy `client_address[0] == "127.0.0.1"`, i odrzuca resztę z kodem 403 — na wypadek, gdyby ktoś
> uruchomił serwer za pośrednikiem. Trzecia: żądania `POST` bez nagłówka
> `Origin: http://127.0.0.1:<port>` są odrzucane, żeby strona otwarta w tej samej przeglądarce
> nie mogła zapisać pliku w tle.

**Zmiana vs. stan obecny**: dziś projekt nie ma żadnego kodu, który cokolwiek zapisuje. Ta
zmiana wprowadza pierwszy taki kod, dlatego ograniczenia są opisane wprost, a nie domyślne.

## Architektura

```
tools/panel/
  serwer.py      # lokalny serwer HTTP: statyki panelu + /api/wczytaj + /api/zapisz
  panel.html     # interfejs
  panel.js       # logika formularza, walidacja po stronie przegladarki, podglad karty
  panel.css      # style panelu (panel NIE korzysta z custom.css witryny)
data/
  wina.json      # plik edytowany
  wina.json.bak  # kopia poprzedniej wersji, nadpisywana przy kazdym zapisie
```

**Dlaczego osobny serwer, a nie `wsgi.py`**: produkcyjny serwer ma pozostać serwerem plików
statycznych bez prawa zapisu. Rozdzielenie sprawia, że żaden błąd w konfiguracji wdrożenia nie
wystawi zapisu do internetu — kod zapisujący fizycznie nie istnieje w aplikacji produkcyjnej.
Zapisane w `.ai/GUARDRAILS.md` → „Panel redakcyjny poza aplikacją produkcyjną".

**Dlaczego biblioteka standardowa, a nie Flask**: `http.server` wystarcza do dwóch endpointów,
a projekt celowo nie ma `requirements.txt` (`.ai/GUARDRAILS.md` → BLOCK #6). Panel ma działać
po `git clone` i `python3`, bez instalowania czegokolwiek.

### API

| Metoda | Ścieżka | Odpowiedź |
|---|---|---|
| `GET` | `/` | `panel.html` |
| `GET` | `/api/wczytaj` | treść `data/wina.json` + lista slugów z `attached_assets/photos/` + lista plików `wina/*.html` |
| `POST` | `/api/zapisz` | `{"ok": true, "pozycji": 6}` albo `400` z listą błędów walidacji |

Serwer oddaje też pliki z `attached_assets/photos/` i `assets/css/style.css`, żeby podgląd karty
wyglądał jak w sklepie.

### Walidacja

Ta sama lista reguł działa w przeglądarce (od razu, przy polu) i na serwerze (przed zapisem).
Serwer jest instancją rozstrzygającą — przeglądarce nie wolno ufać nawet lokalnie.

| Reguła | Komunikat |
|---|---|
| `id` niepuste, unikalne, `[a-z0-9-]+` | „Identyfikator musi być unikalny; dozwolone małe litery, cyfry i myślnik" |
| `nazwa`, `opis` niepuste | „Pole wymagane" |
| `kategoria` ∈ `kategorie` | „Nieznana kategoria" |
| `odmiana_slug` wskazuje istniejący `wina/<slug>.html` | „Nie ma strony odmiany o tym adresie" |
| `zdjecie` istnieje w `attached_assets/photos/<slug>.jpg` | „Nie ma takiego zdjęcia" |
| `cena_brutto` > 0, najwyżej 2 miejsca po przecinku | „Cena musi być liczbą dodatnią" |
| `rabat_procent` 0–99 | „Rabat poza zakresem 0–99" |
| `pojemnosc_ml` > 0 | „Pojemność musi być liczbą dodatnią" |
| brak pól spoza schematu | „Nieznane pole: …" |

Zapis odrzucony w całości, jeśli którakolwiek pozycja nie przejdzie — plik nigdy nie zostaje
w stanie częściowo poprawnym.

### Bezpieczeństwo

1. `bind` wyłącznie na `127.0.0.1` (nie `0.0.0.0`).
2. Sprawdzenie `client_address[0] == "127.0.0.1"` przy każdym żądaniu; inaczej 403.
3. `POST` wymaga nagłówka `Origin: http://127.0.0.1:<port>`; inaczej 403.
4. Serwer oddaje pliki **tylko** z trzech miejsc: `tools/panel/`, `attached_assets/photos/`,
   `assets/css/`. Ścieżki są normalizowane i sprawdzane, czy nie wychodzą poza katalog projektu.
5. Zapis dotyczy jednego pliku — `data/wina.json`. Ścieżka jest stała w kodzie, nie z żądania.
6. Przed zapisem powstaje `data/wina.json.bak`; zapis jest atomowy (`os.replace`).

## Configuration

Port: `8765`, do zmiany przez `--port`. Brak zmiennych środowiskowych, brak zależności.

```bash
python3 tools/panel/serwer.py            # http://127.0.0.1:8765
python3 tools/panel/serwer.py --port 9000
```

## UI/UX

- Panel jest po polsku, jednoekranowy: lista pozycji + rozwijany formularz.
- Wskaźnik „niezapisane zmiany" i blokada zamknięcia karty przy niezapisanych zmianach
  (`beforeunload`).
- Po zapisie komunikat przypomina o commicie i wdrożeniu — panel niczego nie publikuje.
- **Panel nie używa `assets/css/custom.css` ani motywów witryny.** Ma własny, neutralny styl;
  wyjątkiem jest podgląd karty, który celowo ładuje `assets/css/style.css`, żeby wyglądać
  identycznie jak sklep.
- Bez `alert()` i `confirm()` — komunikaty w interfejsie. Powód praktyczny: te okna blokują
  automatyzację przeglądarki (`.ai/GUARDRAILS.md` → Allowed exceptions #1).

## Implementation Checklist

- [ ] Inject standards (`content/wina-json`, `frontend/js-conventions`)
- [ ] `tools/panel/serwer.py` — routing, `/api/wczytaj`, statyki z trzech katalogów
- [ ] `serwer.py` — walidacja po stronie serwera (tabela wyżej)
- [ ] `serwer.py` — `/api/zapisz`: kopia `.bak`, zapis atomowy, odpowiedzi błędów
- [ ] `serwer.py` — trzy zabezpieczenia dostępu (bind, adres klienta, `Origin`)
- [ ] `panel.html` + `panel.css` — lista i formularz
- [ ] `panel.js` — walidacja przy polach, stan „niezapisane zmiany", `beforeunload`
- [ ] `panel.js` — podgląd karty przez `renderProductCard()` z `assets/js/main.js`
- [ ] Obsługa nowej kategorii (dopisanie do `kategorie`) z ostrzeżeniem
- [ ] `data/wina.json.bak` w `.gitignore`
- [ ] Ręczny test: zmiana ceny, dodanie pozycji, usunięcie, próba zapisu błędnych danych
- [ ] Ręczny test: sprawdzenie, że `http://<adres-w-LAN>:8765` nie odpowiada
- [ ] Krótka instrukcja uruchomienia w `AGENTS.md` → Commands (do uzgodnienia z Właścicielem)
- [ ] `/sync-standards`

## Otwarte decyzje

1. **Soki a `odmiana_slug`** (Story 2) — pole wymagane dla wszystkich pozycji, czy opcjonalne
   dla kategorii innych niż wino? Do czasu decyzji: wymagane.
2. **Czy panel ma edytować `stawka_vat`** — dziś zakładam, że nie: to zmiana raz na kilka lat
   i wymaga też poprawienia etykiety „VAT (23%)" w `index.html` (`TODO.md` #4).

## Changelog

### 2026-09-02
- Pierwsza wersja specyfikacji.
