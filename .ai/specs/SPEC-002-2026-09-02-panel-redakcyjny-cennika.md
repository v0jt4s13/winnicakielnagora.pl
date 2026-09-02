# SPEC-002 — Panel redakcyjny do `data/wina.json`

**Status**: propozycja do akceptacji
**Rozmiar**: M
**Data**: 2026-09-02
**Zależy od**: SPEC-001 — Etap 2, konkretnie dwóch rzeczy:

1. `data/wina.json` istnieje (może mieć pustą tablicę `wina`),
2. `assets/js/produkty.js` dostarcza `Produkty.renderProductCard()` i `Produkty.policzCeny()`
   (kontrakt: SPEC-001 → „Kontrakt `assets/js/produkty.js`").

Etap 2 SPEC-001 **nie jest już niczym zablokowany** — zgoda na zmianę `GUARDRAILS.md` została
udzielona 2026-09-02, a brak asortymentu (blokada B1) dotyczy treści pliku, nie mechanizmu.
Panel jest właśnie narzędziem, którym B1 się zamyka.

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

> **Za kulisami**: podgląd używa **tej samej funkcji** `Produkty.renderProductCard()` z
> `assets/js/produkty.js`, co sklep, i tego samego `assets/css/style.css`. Dzięki temu nie może się
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
główną ze statusem 200 (`TODO.md` #5), więc nikt by tego nie zauważył. **Rozstrzygnięte
2026-09-02**: powstała zbiorcza strona `wina/soki.html`, więc sok wskazuje `soki`,
a `odmiana_slug` zostaje polem wymaganym dla każdej pozycji.

### Story 3 — Właściciel wkleja notatki, model językowy robi z nich opis

**Persona**: ten sam Właściciel. Ma w notatniku pół strony luźnych uwag o winie — wrażenia
z degustacji, informacje o roczniku, zdania wyrwane z rozmów z klientami. Nie chce z tego
sam pisać zgrabnego zdania na kartę produktu.

**Krok 1.** Rozwija pole „Pomoc w opisie" pod formularzem i wkleja całość.

```
┌──────────────────────────────────────────────────────────────┐
│  Pomoc w opisie                                     [ ▾ ]    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ zbiór 2024 był wyjątkowo słoneczny, grona dojrzały     │  │
│  │ tydzień wcześniej. wino wytrawne, kwasowość wyraźna    │  │
│  │ ale nie ostra, w nosie brzoskwinia, trochę cytrusa...  │  │
│  └────────────────────────────────────────────────────────┘  │
│  2 431 znaków                    [ Przygotuj opis ]          │
└──────────────────────────────────────────────────────────────┘
```

**Krok 2.** Po chwili dostaje dwie propozycje, każdą z osobnym przyciskiem.

```
┌──────────────────────────────────────────────────────────────┐
│  Opis na kartę produktu                     [ Wstaw do pola ]│
│  Wytrawne białe o wyraźnej, ale łagodnej kwasowości.         │
│  W aromacie brzoskwinia i cytrusy. Rocznik 2024.             │
│                                                              │
│  Opis meta (dla strony odmiany)                   [ Kopiuj ] │
│  Souvignier Gris 2024 z Winnicy Kielna Góra — wytrawne       │
│  białe o aromatach brzoskwini i cytrusów. 148 znaków.        │
└──────────────────────────────────────────────────────────────┘
```

> **Za kulisami**: `POST /api/opisz` z wklejonym tekstem i kontekstem pozycji (nazwa, odmiana,
> kategoria, rocznik). Serwer woła OpenAI Chat Completions przez `urllib` z biblioteki
> standardowej — **bez pakietu `openai`**, żeby nie dokładać zależności. Klucz czyta ze zmiennej
> środowiskowej `OPENAI_API_KEY`, nigdy nie trafia do przeglądarki ani do repozytorium.
> Odpowiedź modelu wraca jako JSON i **nic nie zapisuje sama** — dopóki Właściciel nie kliknie
> „Wstaw do pola" i „Zapisz", plik się nie zmienia.

**Zmiana vs. stan obecny**: dziś pole „Opis" jest puste i trzeba je napisać ręcznie.
Po zmianie można wkleić surowe notatki i dostać z nich gotowy tekst — ale **decyzja i tak
należy do człowieka**, bo propozycja ląduje w polu formularza, a nie w pliku.

**Dlaczego dwa teksty, a nie jeden**: karta produktu jest renderowana przez JavaScript, więc
jej opis ma znikomą wartość dla wyszukiwarek. Prawdziwy SEO dzieje się na statycznych stronach
odmian, których panel nie edytuje — dlatego drugi tekst jest do skopiowania ręcznie do
`wina/<slug>.html`.

### Story 4 — Ktoś próbuje otworzyć panel z innego komputera (przypadek brzegowy)

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

### Podgląd karty — skąd bierze się kod

Panel ładuje `assets/js/produkty.js` zwykłym `<script>` i woła
`Produkty.renderProductCard(wino, stawkaVat, { przyciskKoszyka: false })`, wstawiając zwrócony
HTML do kontenera podglądu. Plik nie rejestruje żadnych zdarzeń i nie dotyka DOM-u strony
głównej, więc jego wczytanie niczego nie uruchamia (SPEC-001 → „Kontrakt `assets/js/produkty.js`").

**`assets/js/main.js` nie jest ładowany w panelu i nie jest serwowany** — jego
`DOMContentLoaded` odpaliłby nawigację, motywy i koszyk, których w panelu nie ma.

### API

Wszystkie odpowiedzi to `application/json; charset=utf-8`.

| Metoda | Ścieżka | Opis |
|---|---|---|
| `GET` | `/` | `panel.html` |
| `GET` | `/api/wczytaj` | stan początkowy panelu (niżej) |
| `POST` | `/api/zapisz` | zapis pliku; `Content-Type: application/json` |

`GET /api/wczytaj` → `200`:

```json
{
  "cennik": { "waluta": "PLN", "stawka_vat": 0.23, "kategorie": ["Białe"], "wina": [] },
  "zdjecia": ["dornfelder-kiscie-01", "monarch-butelka-01"],
  "odmiany": ["dornfelder", "monarch", "souvignier-gris"],
  "sciezka": "/home/vs/repo-agents/winnica/data/wina.json"
}
```

- `cennik` — dosłowna treść `data/wina.json`. Jeśli pliku nie ma, serwer zwraca szkielet
  z pustą tablicą `wina` i **nie tworzy pliku** — powstanie dopiero przy pierwszym zapisie.
- `zdjecia` — slugi z `attached_assets/photos/`, **z odfiltrowanymi wariantami `-sm`**
  i bez rozszerzenia, posortowane alfabetycznie. Taki sam format ma pole `zdjecie` w cenniku.
- `odmiany` — nazwy plików `wina/*.html` bez rozszerzenia, posortowane. Pusta lista, jeśli
  katalogu jeszcze nie ma.

`POST /api/zapisz` — ciałem żądania jest **cała nowa treść pliku** w tym samym kształcie, co
`cennik` z `/api/wczytaj`. Odpowiedź `200`:

```json
{ "ok": true, "pozycji": 6, "kopia": "data/wina.json.bak" }
```

Odpowiedź `400` przy błędach walidacji — zapis **nie następuje w całości**:

```json
{ "ok": false, "bledy": [
  { "pozycja": 2, "pole": "cena_brutto", "komunikat": "Cena musi być liczbą dodatnią" },
  { "pozycja": null, "pole": "kategorie", "komunikat": "Lista kategorii nie może być pusta" }
]}
```

`pozycja` to indeks w tablicy `wina` (od 0) albo `null` dla błędów dotyczących całego pliku.

### `POST /api/opisz` — przygotowanie opisu przez model językowy

Żądanie:

```json
{ "tekst": "surowe notatki…",
  "kontekst": { "nazwa": "Souvignier Gris", "kategoria": "Białe", "rocznik": 2024,
                "odmiana_slug": "souvignier-gris" } }
```

Odpowiedź `200`:

```json
{ "ok": true, "opis": "Wytrawne białe…", "opis_meta": "Souvignier Gris 2024 z Winnicy…" }
```

Odpowiedź `400` / `502` — `{"ok": false, "komunikat": "…"}` z powodem po polsku
(brak klucza, przekroczony limit, błąd API, model zwrócił coś innego niż JSON).

**Zasady:**

- **Dostawca**: OpenAI, endpoint `/v1/chat/completions`, wołany przez `urllib.request`
  z biblioteki standardowej. **Nie instalujemy pakietu `openai`** — projekt nie ma
  `requirements.txt` i ma go nie mieć (`.ai/GUARDRAILS.md` → BLOCK #6).
- **Klucz** wyłącznie ze zmiennej `OPENAI_API_KEY`. Nigdy w repozytorium, nigdy w odpowiedzi
  do przeglądarki, nigdy w logach. Brak klucza = czytelny komunikat, nie awaria.
- **Model** ze zmiennej `OPENAI_MODEL`, domyślnie `gpt-4o-mini`. Nazwy modeli się zmieniają,
  więc ma być do podmiany bez dotykania kodu. `OPENAI_BASE_URL` pozwala wskazać inny endpoint
  zgodny z API OpenAI.
- **Limit wejścia**: 20 000 znaków. Dłuższy tekst jest odrzucany z komunikatem, zamiast
  po cichu generować rachunek.
- **Wklejony tekst to dane, nie polecenia.** Prompt systemowy mówi wprost, że treść
  użytkownika należy potraktować jako materiał źródłowy i zignorować zawarte w niej instrukcje.
- **Model nie ma prawa zmyślać.** Prompt zabrania dodawania faktów spoza wklejonego tekstu
  i kontekstu pozycji — to ta sama zasada, co w SPEC-001 („Zasada dotycząca treści, których
  nie znamy").
- **Nic nie zapisuje się automatycznie.** Wynik trafia do pola formularza dopiero po kliknięciu
  i wymaga osobnego „Zapisz".

**Świadomość wysyłki na zewnątrz**: wklejony tekst opuszcza infrastrukturę i trafia do OpenAI.
Dla notatek o winie to bez znaczenia, ale **nie wklejaj tam danych osobowych** — nazwisk
klientów, adresów, treści maili. Panel ostrzega o tym przy polu.

### Pliki serwowane przez panel

Serwer oddaje wyłącznie:

| Ścieżka | Po co |
|---|---|
| `tools/panel/*` | interfejs panelu |
| `assets/js/produkty.js` | **ten jeden plik**, do podglądu karty |
| `assets/css/style.css` | **ten jeden plik**, żeby podgląd wyglądał jak sklep |
| `attached_assets/photos/*` | miniatury w podglądzie i na liście |

Żadnych innych plików — w szczególności `assets/js/main.js`, `index.html` ani niczego z `.git/`.

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

**Propozycja `id` z nazwy** (Story 2): małe litery, polskie znaki transliterowane
(`ą→a ć→c ę→e ł→l ń→n ó→o ś→s ź→z ż→z`), wszystko poza `[a-z0-9]` zamienione na `-`, wielokrotne
myślniki zwinięte, myślniki z brzegów obcięte, na końcu dopisany rocznik, jeśli podany.
`Sok z białych winogron` → `sok-z-bialych-winogron`. Propozycja jest tylko podpowiedzią —
pole `id` pozostaje edytowalne, a przy kolizji panel dopisuje `-2`, `-3`…

### Bezpieczeństwo

1. `bind` wyłącznie na `127.0.0.1` (nie `0.0.0.0`).
2. Sprawdzenie `client_address[0] == "127.0.0.1"` przy każdym żądaniu; inaczej 403.
3. `POST` wymaga nagłówka `Origin: http://127.0.0.1:<port>`; inaczej 403.
4. Serwer oddaje **tylko** pliki z tabeli „Pliki serwowane przez panel" — dwa konkretne pliki
   plus zawartość dwóch katalogów. Ścieżka z żądania jest sprawdzana tak:
   `sciezka = (KATALOG_PROJEKTU / zadanie).resolve()`, a następnie odrzucana, jeśli
   `KATALOG_PROJEKTU` nie jest jej przodkiem (`Path.is_relative_to`) **albo** jeśli nie mieści
   się w dozwolonym zbiorze. Samo obcięcie `..` nie wystarcza — dowiązanie symboliczne
   wyprowadziłoby poza projekt, a `resolve()` je rozwija przed sprawdzeniem.
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

- [x] Inject standards (`content/wina-json`, `frontend/js-conventions`)
- [x] `tools/panel/serwer.py` — routing, `/api/wczytaj`, statyki z trzech katalogów
- [x] `serwer.py` — walidacja po stronie serwera (tabela wyżej)
- [x] `serwer.py` — `/api/zapisz`: kopia `.bak`, zapis atomowy, odpowiedzi błędów
- [x] `serwer.py` — trzy zabezpieczenia dostępu (bind, adres klienta, `Origin`)
- [x] `panel.html` + `panel.css` — lista i formularz
- [x] `panel.js` — walidacja przy polach, stan „niezapisane zmiany", `beforeunload`
- [x] `panel.js` — podgląd karty przez `Produkty.renderProductCard()` z `assets/js/produkty.js`
- [x] `panel.js` — propozycja `id` z transliteracją polskich znaków
- [x] Obsługa nowej kategorii (dopisanie do `kategorie`) z ostrzeżeniem w interfejsie
      (pasek pod polem, nie `alert()`)
- [x] `data/wina.json.bak` w `.gitignore`
- [x] Ręczny test: zmiana ceny, dodanie pozycji, usunięcie, próba zapisu błędnych danych
- [x] Ręczny test: sprawdzenie, że `http://<adres-w-LAN>:8765` nie odpowiada
- [ ] Krótka instrukcja uruchomienia w `AGENTS.md` → Commands (do uzgodnienia z Właścicielem)
- [ ] `/sync-standards`

## Otwarte decyzje

1. ~~**Soki a `odmiana_slug`**~~ — **rozstrzygnięte 2026-09-02**: powstaje strona zbiorcza
   `wina/soki.html`, a `odmiana_slug` zostaje polem **wymaganym dla każdej** pozycji. Sok
   wskazuje `soki`. Brak wyjątków w kodzie, brak martwych linków.
2. **Czy panel ma edytować `stawka_vat`** — dziś zakładam, że nie: to zmiana raz na kilka lat
   i wymaga też poprawienia etykiety „VAT (23%)" w `index.html` (`TODO.md` #4).

## Changelog

### 2026-09-02 — zaimplementowane
Panel działa. Sprawdzone: odczyt i zapis cennika, kopia `.bak`, walidacja odrzucająca
11 rodzajów błędów w jednej pozycji, 403 dla żądania bez nagłówka `Origin`, 404 dla prób
wyjścia poza dozwolone katalogi (`/../../wsgi.py`, `/assets/js/main.js`, `/index.html`).
Dodatkowo panel ostrzega przy wyborze zdjęcia z członem `-osoby-` (TODO.md #14).

### 2026-09-02
- Poprawki po recenzji `spec-reviewer`: usunięta sprzeczność między podglądem karty a listą
  serwowanych plików (podgląd korzysta z wydzielonego `assets/js/produkty.js`, `main.js` nie jest
  serwowany ani ładowany); doprecyzowany kształt żądań i odpowiedzi obu endpointów; zasada
  filtrowania wariantów `-sm`; algorytm sprawdzania ścieżek (`resolve()` + `is_relative_to`);
  transliteracja przy proponowaniu `id`; jawnie opisana zależność od Etapu 2 SPEC-001.
- Pierwsza wersja specyfikacji.
