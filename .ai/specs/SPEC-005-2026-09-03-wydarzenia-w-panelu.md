# Wydarzenia redagowane w panelu

## Overview

Właściciel ma móc dodać wpis o wydarzeniu (tytuł, treść, data od, data do) w panelu
redakcyjnym, a wpis ma pokazać się w sekcji `#wydarzenia` na stronie głównej **tylko wtedy,
gdy dzisiejsza data mieści się w przedziale `[data_od, data_do]`**. Poza tym przedziałem
wpis nie istnieje dla odwiedzającego.

Wzorzec jest już w projekcie i zostaje powtórzony: `data/wina.json` + moduł `cennik.py` +
akcje panelu + render w `main.js`. Wydarzenia dostają własny plik, własny moduł i własne
akcje — nie doklejamy ich do cennika, bo to inny byt, o innym cyklu życia i innej walidacji.

### Czego ta zmiana świadomie nie robi

- **Nie ma godzin.** Granice są dzienne, w strefie `Europe/Warsaw`.
- **Nie ma powtarzalności ani kalendarza.** Wpis to jeden przedział dat, nie cykl.

> Dwa wcześniejsze ograniczenia zostały zniesione na wniosek Właściciela (2026-09-03):
> wpis ma własną **datę publikacji** (można zapowiedzieć wydarzenie z wyprzedzeniem)
> oraz **zdjęcie**. Szczegóły niżej; poprzedni zapis mówił, że jednego i drugiego nie ma.

## User Stories

### 1. Właściciel dodaje wydarzenie na najbliższy weekend

**Persona:** Właściciel winnicy, obsługuje panel przez przeglądarkę, nie zna się na kodzie.
Chce ogłosić dzień otwarty i mieć pewność, że wpis sam zniknie po weekendzie.

1. Wchodzi do panelu i widzi nową sekcję pod cennikiem.

   ```text
   ┌──────────────────────────────────────────────────────────┐
   │  Wydarzenia (2)   data/wydarzenia.json                   │
   │                   [Odrzuć zmiany] [Zapisz] [+ Dodaj wpis]│
   ├──────────────────────────────────────────────────────────┤
   │  Dzień otwarty        10.09 – 12.09          aktywne     │
   │  Winobranie 2026      20.09 – 05.10          przyszłe    │
   └──────────────────────────────────────────────────────────┘
   ```

   **Za kulisami:** `panel.js` woła `GET /tools/panel/api/wydarzenia-wczytaj`, które zwraca
   **wszystkie** wpisy (także nieaktywne) — panel jest narzędziem redakcyjnym i musi widzieć
   całość. Znacznik „aktywne / przyszłe / zakończone" liczy przeglądarka z dat, wyłącznie
   informacyjnie; źródłem prawdy o widoczności jest serwer.

   > **Zmiana vs. stan obecny:** dziś panel ma jedną sekcję i jedną parę przycisków
   > „Zapisz" / „Odrzuć zmiany" w sticky nagłówku (`.pasek`), działających na całym cenniku.
   > Po zmianie każda sekcja ma **własną** parę przycisków we własnym nagłówku, a sticky pasek
   > przestaje należeć do cennika — szczegóły w Architecture → „Panel z dwiema sekcjami".

2. Klika „+ Dodaj wpis" i wypełnia formularz. Układ jest kopią formularza pozycji cennika:
   „Usuń" siedzi w nagłówku sekcji formularza, a utrwalenie idzie przyciskiem „Zapisz"
   z nagłówka sekcji „Wydarzenia".

   ```text
   ┌──────────────────────────────────────────────┐
   │  Wydarzenie                    [ Usuń wpis ] │
   ├──────────────────────────────────────────────┤
   │  Tytuł     [ Dzień otwarty                 ] │
   │  Treść     [ Zapraszamy na zwiedzanie...   ] │
   │            [                               ] │
   │  Data od   [ 2026-09-10 ]                    │
   │  Data do   [ 2026-09-12 ]                    │
   └──────────────────────────────────────────────┘
   ```

   **Za kulisami:** zmiany żyją w stanie `panel.js` do momentu „Zapisz". Zapis to
   `POST /tools/panel/api/wydarzenia-zapisz` z całą listą; serwer waliduje przez
   `wydarzenia.waliduj()` i zapisuje atomowo, robiąc kopię `.bak` — jak `cennik.zapisz()`.

3. Wchodzi na stronę główną 10 września — wpis jest w sekcji „Wydarzenia i Degustacje".
   13 września wpis znika sam, bez logowania do panelu.

### 2. Odwiedzający otwiera stronę, gdy nic się nie dzieje

**Persona:** osoba planująca wizytę, trafia na stronę w martwym okresie między wydarzeniami.

1. Sekcja `#wydarzenia` wygląda dokładnie tak jak dziś:

   ```text
   ┌──────────────────────────────────────────────┐
   │ [zdjęcie]  │  Degustacje po umówieniu        │
   │            │  Nie prowadzimy stałego         │
   │            │  kalendarza wydarzeń...         │
   └──────────────────────────────────────────────┘
   ```

   **Za kulisami:** `/data/wydarzenia.json` zwraca pustą tablicę, `initWydarzenia()` nie
   wstawia niczego i zostawia `#lista-wydarzen` z atrybutem `hidden`.

   > **Zmiana vs. stan obecny:** żadna. To jest wymaganie, nie efekt uboczny — obecna treść
   > („nie prowadzimy stałego kalendarza") jest prawdziwa dokładnie wtedy, gdy lista jest
   > pusta, więc musi zostać stanem domyślnym.

2. Gdy jest co najmniej jedno aktywne wydarzenie, nad istniejącą kartą degustacji pojawia się
   lista wpisów. Treść o degustacjach zostaje — to osobna, stała oferta.

| Stan danych | Co widzi odwiedzający |
|---|---|
| brak pliku / błąd składni | obecna karta degustacji, `console.error`, **żadnego** komunikatu o błędzie |
| pusta lista albo same nieaktywne wpisy | obecna karta degustacji, bez zmian |
| ≥ 1 aktywny wpis | lista wpisów + obecna karta degustacji |

**Dlaczego cicha porażka, inaczej niż w sklepie:** brak cennika to zepsuty sklep i trzeba
o tym powiedzieć. Brak wydarzeń to normalny stan winnicy — komunikat o błędzie byłby tu
szumem dla odwiedzającego.

### 3. Właściciel wpisuje datę „od" późniejszą niż „do"

**Persona:** ten sam Właściciel, spieszy się, myli pola.

1. Klika „Zapisz" z `data_od = 2026-10-05`, `data_do = 2026-09-20`.

   ```text
   ┌──────────────────────────────────────────────┐
   │  ✗ Nie zapisano — popraw 1 błąd:             │
   │    Wydarzenie 1 · data_do:                   │
   │    „data do" nie może być wcześniejsza niż   │
   │    „data od"                                 │
   └──────────────────────────────────────────────┘
   ```

   **Za kulisami:** `wydarzenia.waliduj()` zwraca listę błędów w formacie `cennik._blad()`
   (`{pozycja, pole, komunikat}`), API odpowiada `400`, `panel.js` renderuje je w tym samym
   `#komunikat`, którym pokazuje błędy cennika. **Plik nie zostaje ruszony** — walidacja jest
   przed zapisem, tak jak w cenniku.

   > **Zmiana vs. stan obecny:** żadna nowa mechanika. To jest test, czy nowy moduł trzyma
   > kontrakt błędów, który panel już umie wyświetlać.

2. Przypadki brzegowe do pokrycia walidacją: `data_od == data_do` (poprawne, wydarzenie
   jednodniowe), pusty tytuł, pusta treść, data w złym formacie, data nieistniejąca
   (`2026-02-30`), zduplikowane `id`.

## Warianty widoczności

Niech `dzis` to data w `Europe/Warsaw` w formacie `YYYY-MM-DD`, a `poczatek` to
`data_publikacji_od`, jeśli pole jest wypełnione, albo `data_od`, jeśli puste.

| Warunek | Wpis na stronie |
|---|---|
| `poczatek <= dzis <= data_do` | **widoczny** |
| `dzis < poczatek` | ukryty (jeszcze nie zapowiadamy) |
| `dzis > data_do` | ukryty (wydarzenie się skończyło) |

Granice są domknięte z obu stron: w dniu `poczatek` i w dniu `data_do` wpis jest widoczny.

**Rozdzielenie zapowiedzi od terminu.** `data_od` i `data_do` opisują, **kiedy wydarzenie
się odbywa** — i to one trafiają do zakresu dat pokazywanego odwiedzającemu.
`data_publikacji_od` mówi wyłącznie, **od kiedy wpis ma być widoczny**. Puste pole zachowuje
poprzednie zachowanie (wpis pojawia się w dniu rozpoczęcia), więc wpisy sprzed tej zmiany
działają bez migracji.

Koniec publikacji celowo nie ma osobnego pola: wpis znika po `data_do`, bo zakończone
wydarzenie nie ma czego ogłaszać.
Daty w ISO `YYYY-MM-DD` porównujemy jako napisy — dla tego formatu porządek leksykograficzny
jest tożsamy z chronologicznym, więc nie ma potrzeby parsowania.

## Architecture

### Gdzie mieszka logika — i dlaczego akurat tam

`.ai/GUARDRAILS.md` → „Architectural boundaries" #3 mówi wprost: **`wsgi.py` poza panelem
redakcyjnym NIGDY nie dostaje logiki biznesowej**. Nowa trasa `/data/wydarzenia.json` jest
publiczna, więc filtr dat **nie może** wylądować w handlerze.

Rozstrzygnięcie: filtrowanie to czysta funkcja w `wydarzenia.py`:

```python
def dzis_w_winnicy() -> str:            # "YYYY-MM-DD" w Europe/Warsaw
def aktywne(dane: dict, dzis: str | None = None) -> dict:
    """Zwraca {"wydarzenia": [...]} zawężone do wpisów widocznych danego dnia.
    Bez argumentu `dzis` liczy dzień sam — argument istnieje dla testów."""
```

Handler w `wsgi.py` ma wtedy zero logiki dat: wczytuje, woła `aktywne()`, serializuje.
To nie jest wyjątek od reguły #3, tylko jej spełnienie — `wsgi.py` zostaje routerem.
Guardrail #4 (`tools/` nigdy importowane przez `wsgi.py`) też jest spełniony: moduł mieszka
w katalogu głównym obok `cennik.py`, a `tools/panel/serwer.py` importuje go w drugą stronę.

### Pliki

- **`wydarzenia.py`** (nowy, w korzeniu obok `cennik.py`) — odczyt, walidacja, zapis, filtr
  dat. Nie zna HTTP. Kopia struktury `cennik.py`: `zapewnij_plik()`, `wczytaj()`, `waliduj()`,
  `zapisz()`, `opis_kopii()`, zapis atomowy przez `tempfile` + `os.replace`, prawa `0o640`,
  kopia `.bak` przed nadpisaniem. Dodatkowo `dzis_w_winnicy()` i `aktywne()` opisane wyżej
  oraz `stan_poczatkowy()` zwracające `{"wydarzenia": ..., "sciezka": str(WYDARZENIA)}` —
  panel pokazuje w nagłówku sekcji ścieżkę realnie edytowanego pliku, tak jak robi to dziś
  dla cennika (`panel.js`: `qs("#sciezka").textContent = dane.sciezka`). Bez tego pola
  nagłówek musiałby zgadywać, a na produkcji jest to ścieżka spoza repozytorium.
  Ścieżka robocza: `WYDARZENIA_SCIEZKA`, domyślnie `data/wydarzenia.json` z repozytorium.
  **Powód jest ten sam co przy cenniku:** wdrożenie nie może nadpisać wpisów zrobionych
  panelem (TODO #26, wariant A).

- **`data/wydarzenia.json`** (nowy) — wersja startowa w repozytorium: `{"wydarzenia": []}`.

- **`wsgi.py`**:
  - nowa trasa publiczna `GET /data/wydarzenia.json` — woła `wydarzenia.zapewnij_plik()`
    (dokładnie jak `zywy_cennik()` dla cennika), potem `aktywne()`, `Cache-Control: no-store`.
    Błąd składni pliku → `{"wydarzenia": []}` i `500`, bez wywalania strony.
  - dwie nowe gałęzie w `panel_api` (dispatcher po `<akcja>`): `wydarzenia-wczytaj` (GET,
    **wszystkie** wpisy) i `wydarzenia-zapisz` (POST, walidacja + zapis).

- **`tools/panel/serwer.py`** — **uwaga, inna konwencja niż `wsgi.py`**: nie ma dispatchera,
  są dosłowne porównania ścieżek (`sciezka == "/api/wczytaj"`,
  `sciezka not in ("/api/zapisz", "/api/opisz")`). Do dopisania konkretnie:
  `"/api/wydarzenia-wczytaj"` w `do_GET` oraz `"/api/wydarzenia-zapisz"` w `do_POST`
  (dołożyć do krotki dozwolonych ścieżek).
  **Model bezpieczeństwa obu wejść jest różny i tak zostaje:** `wsgi.py` chroni panel HTTP
  Basic Auth, `serwer.py` nasłuchuje wyłącznie na `127.0.0.1` i hasła nie ma.

- **`assets/js/main.js`** — nowa funkcja `initWydarzenia()` zgodna ze wzorcem `initX()`.
  Pobiera `${KORZEN}data/wydarzenia.json` przez `fetch` z `cache: "no-store"` (jak
  `wczytajCennik()`), przy błędzie `console.error` i cichy powrót. **Zero logiki dat** —
  renderuje to, co przyszło. Wywołanie ląduje w `DOMContentLoaded` w części asynchronicznej,
  obok `renderSklep()`; kolejność względem `initScrollReveal()` opisana niżej.

- **`index.html`** — w sekcji `#wydarzenia`, **nad** istniejącą kartą degustacji:
  `<div id="lista-wydarzen" class="space-y-5 mb-12" data-reveal hidden></div>`.
  Markup wpisu tworzy JS. Istniejąca karta degustacji zostaje nietknięta.

- **`assets/css/custom.css`** — jedna nowa reguła (patrz UI/UX; klasy `whitespace-pre-line`
  **nie ma w bundlu Tailwinda**, więc nie da się jej użyć).

### Panel z dwiema sekcjami

`tools/panel/panel.js` ma dziś jeden globalny stan (`cennik`, `wybrany`, `zmienione`) i jedną
parę `#zapisz` / `#odrzuc` w sticky pasku. Dokładanie drugiej sekcji wymaga rozstrzygnięć:

| Element | Cennik (istniejący) | Wydarzenia (nowy) |
|---|---|---|
| stan | `cennik`, `wybrany`, `zmienione` | `wydarzenia`, `wybraneWydarzenie`, `zmienioneWydarzenia` |
| zapis / odrzuć | `#zapisz`, `#odrzuc` | `#zapisz-wydarzenia`, `#odrzuc-wydarzenia` |
| lista | `#lista` | `#lista-wydarzen-panel` |
| formularz | `#formularz` | `#formularz-wydarzenia` |
| komunikat | `#komunikat` | **ten sam** `#komunikat` |
| wskaźnik zmian | `#stan-zmian` | **ten sam** `#stan-zmian` |

- **Sticky pasek przestaje należeć do cennika.** `h1` zmienia się z „Cennik" na
  „Panel redakcyjny", a `#sciezka` i para przycisków cennika przenoszą się do nagłówka
  sekcji „Pozycje". Każda sekcja ma odtąd własny zapis. Bez tego „Zapisz" w sticky pasku
  byłby dwuznaczny.
- **`#komunikat` jest wspólny** — jednocześnie zapisuje się tylko jedna sekcja, a komunikat
  nazywa, której dotyczy. Drugi obszar komunikatów byłby nadmiarem.
- **`#stan-zmian` zostaje jeden, w sticky pasku**, i pokazuje `zmienione || zmienioneWydarzenia`.
  Przyciski zapisu przenoszą się do sekcji, ale ostrzeżenie „masz niezapisaną pracę" dotyczy
  całego panelu i ma być widoczne niezależnie od tego, którą sekcję akurat widać na ekranie.
  Dublowanie wskaźnika do obu nagłówków dałoby dwa miejsca mówiące to samo.
- **`beforeunload`** rozszerza istniejący warunek do `zmienione || zmienioneWydarzenia`.
- **Zapis jednej sekcji nie dotyka drugiej**: osobne akcje API, osobne pliki, osobna walidacja.

### Zwijanie sekcji

Panel po dodaniu wydarzeń ma pięć sekcji i nie mieści się na ekranie. Nagłówek każdej
**sekcji treściowej** staje się klikalny i chowa albo pokazuje jej zawartość.

- Zwijane są: **Pozycje**, **Wydarzenia**, **Kategorie**.
- **Nie są zwijane sekcje formularzy** (`#sekcja-formularza` i jej odpowiednik dla wydarzeń).
  Mają już własny mechanizm widoczności — pojawiają się po wybraniu pozycji z listy.
  Drugi, niezależny przełącznik dawałby stan „sekcja rozwinięta, ale pusta, bo nic nie wybrano"
  i dwa powody, dla których to samo miejsce bywa puste.
- Markup: w `.naglowek-sekcji` ląduje `<button type="button" class="przelacznik-sekcji"
  aria-expanded="true" aria-controls="<id ciała>">` z tytułem i strzałką, a ciało sekcji jest
  owinięte w `<div class="cialo-sekcji" id="...">`. Przyciski akcji („Zapisz", „Dodaj
  pozycję") zostają **rodzeństwem** przełącznika, nie jego dziećmi — zagnieżdżony `<button>`
  to nieprawidłowy HTML i przestałby działać.
- Obsługa: `initZwijanieSekcji()` w `panel.js` — klik przełącza `hidden` na ciele
  i `aria-expanded` na przycisku.
- **Stan nie jest zapamiętywany.** Po odświeżeniu wszystkie sekcje są rozwinięte. Panel nie
  trzyma niczego w `localStorage` i ta zmiana tego nie otwiera; zwijanie ma skracać przewijanie
  w trakcie pracy, a nie konfigurować panel na stałe.

> To jedyne miejsce, gdzie zmiana rusza istniejący markup i kod panelu.
> **Do wycięcia, jeśli Właściciel woli zostawić sticky pasek cennikowi** — wtedy wydarzenia
> dostają zapis wyłącznie we własnym nagłówku, a pasek zostaje bez zmian.

### Zakres poza dosłownym brzmieniem zadania

Zadanie mówi o „formularzu dodawania wpisów". Spec obejmuje też **edycję i usuwanie**,
bo bez nich wpisy nie dają się poprawić ani sprzątnąć, a `data_do` tylko je ukrywa — plik
rósłby w nieskończoność. **Do wycięcia, jeśli Właściciel uzna to za nadmiar.**

## Data Models

`data/wydarzenia.json`:

```json
{
  "wydarzenia": [
    {
      "id": "dzien-otwarty-2026-09",
      "tytul": "Dzień otwarty",
      "tresc": "Zapraszamy na zwiedzanie winnicy i degustację młodych roczników.",
      "data_od": "2026-09-10",
      "data_do": "2026-09-12"
    }
  ]
}
```

| Pole | Reguła |
|---|---|
| `id` | `^[a-z0-9-]+$`, unikalne w pliku. Nadawane przez panel ze slugu tytułu + licznik przy kolizji (jest już `ZNAKI` i slugifikacja w `panel.js`) |
| `tytul` | niepusty po przycięciu, ≤ 120 znaków |
| `tresc` | niepusta po przycięciu, ≤ 2000 znaków, zwykły tekst (**bez HTML** — patrz niżej) |
| `data_od` | `^\d{4}-\d{2}-\d{2}$` **i** poprawna data kalendarzowa (`datetime.date.fromisoformat`) |
| `data_do` | jak wyżej, dodatkowo `data_do >= data_od` |

Pola opcjonalne:

| Pole | Reguła |
|---|---|
| `data_publikacji_od` | data jak wyżej, dodatkowo `<= data_do`. Puste albo brak = `data_od` |
| `zdjecie` | slug z `attached_assets/photos/` **bez** rozszerzenia i bez `-sm`, dokładnie jak `zdjecie` pozycji cennika. Puste albo brak = wpis bez zdjęcia |

Nieznane pola w pliku → błąd walidacji, jak w cenniku.

**`data_publikacji_od > data_do` jest błędem, nie dziwnym ustawieniem** — taki wpis nigdy
by się nie pokazał, a cisza wyglądałaby jak usterka strony.

**Skąd lista zdjęć w panelu.** `wydarzenia.py` **nie** buduje własnej listy slugów i nie
importuje `cennik.py`: sprawdza po prostu, czy `attached_assets/photos/<slug>.jpg` istnieje.
Panel ma już listę `zdjecia` z `cennik.stan_poczatkowy()` i to jej używa do zbudowania
`<select>` — jedna lista, dwa formularze, zero duplikatu.

**Treść jest zwykłym tekstem i trafia do DOM przez `textContent`, nigdy `innerHTML`.**
Wpis pochodzi z panelu za hasłem, ale to jedyne miejsce w projekcie, gdzie tekst wpisany
przez człowieka ląduje w markupie strony publicznej — `innerHTML` zamieniłby literówkę
w panelu w XSS.

## API Contracts

| Metoda i adres | Kto | Zwraca |
|---|---|---|
| `GET /data/wydarzenia.json` | publicznie | `{"wydarzenia": [...]}` — **tylko aktywne na dziś**, `no-store` |
| `GET /tools/panel/api/wydarzenia-wczytaj` | panel (prod: Basic Auth) | `{"wydarzenia": [...], "sciezka": "<plik roboczy>"}` — wszystkie wpisy |
| `POST /tools/panel/api/wydarzenia-zapisz` | panel (prod: Basic Auth) | `{"ok": true, "pozycji": N, "kopia": "..."}` albo `400` z `{"ok": false, "bledy": [...]}` |
| `GET /api/wydarzenia-wczytaj` | panel lokalny (`serwer.py`, tylko `127.0.0.1`) | jak wyżej |
| `POST /api/wydarzenia-zapisz` | panel lokalny (`serwer.py`, tylko `127.0.0.1`) | jak wyżej |

Format błędu identyczny z cennikiem: `{"pozycja": <int|null>, "pole": <str|null>, "komunikat": <str>}`.

## UI/UX

Wpis na stronie głównej, wewnątrz `#lista-wydarzen`:

Wpis **bez zdjęcia** — zwykła karta z paddingiem, dokładnie jak dotąd:

```text
┌────────────────────────────────────────────────┐
│  10–12 września 2026                           │
│  Dzień otwarty                                 │
│  Zapraszamy na zwiedzanie winnicy…             │
└────────────────────────────────────────────────┘
```

Wpis **ze zdjęciem** — ten sam układ dwukolumnowy, co istniejąca karta degustacji w tej
sekcji (`grid md:grid-cols-2`); na telefonie kolumny składają się do pionu:

```text
┌────────────────────────┬───────────────────────┐
│                        │  1–5 października 2026│
│      [ zdjęcie ]       │  Winobranie 2026      │
│                        │  Zbiory z udziałem…   │
└────────────────────────┴───────────────────────┘
```

- Zdjęcie renderujemy **tylko wtedy, gdy pole `zdjecie` jest wypełnione**.
  Ścieżka: `./attached_assets/photos/<slug>.jpg` — wariant pełny, nie `-sm`.
- **Dlaczego dwie kolumny, a nie pasek nad tekstem.** Biblioteka zdjęć zawiera także kadry
  **pionowe** (np. `dornfelder-kieliszek-01` to 1063×1600). Pasek 16:9 z `object-cover`
  przycinałby je do wąskiego wycinka i ucinał kieliszek w pół. W kolumnie obraz dostaje
  `md:aspect-auto` i wypełnia wysokość tekstu, więc kadr pionowy jest użyteczny.
  Poniżej 768 px zostaje `aspect-video` — na telefonie kolumna i tak jest szeroka.
- Klasy: karta `rounded-md border border-card-border overflow-hidden`, ramka
  `aspect-video md:aspect-auto`, obraz `w-full h-full object-cover`, kolumna tekstu
  `p-8 flex flex-col justify-center`. Wszystkie są w bundlu Tailwinda (sprawdzone).
- `loading="lazy"` i `decoding="async"` — sekcja jest daleko pod zgięciem strony.
- `alt` to tytuł wydarzenia. Zdjęcie niesie treść (co się dzieje), więc puste `alt` byłoby błędem.
- Zakres dat nad tytułem pokazuje **`data_od`–`data_do`**, czyli termin wydarzenia.
  `data_publikacji_od` nie jest nigdzie pokazywana odwiedzającemu — to ustawienie redakcyjne.

- Ramka wpisu: `rounded-md border border-card-border bg-card p-8`.
  **Uwaga na opis:** to nie są „te same klasy co karta degustacji" — tamta ma
  `rounded-md border border-card-border overflow-hidden`, a `p-8` siedzi na jej wewnętrznym
  `<div>`. Wszystkie cztery klasy są w bundlu Tailwinda (`bg-card` używa m.in. `#style-menu`),
  ale w tym zestawieniu wystąpią po raz pierwszy.
- Zakres dat nad tytułem, `text-sm text-muted-foreground`. Formatowanie przez
  `Intl.DateTimeFormat("pl-PL")`; wydarzenie jednodniowe pokazuje jedną datę, nie zakres.
- Tytuł: `font-serif text-2xl font-bold`. Treść: `text-muted-foreground` + nowa klasa
  `.wydarzenie-tresc { white-space: pre-line; }` w `assets/css/custom.css`.
  **Klasy `whitespace-pre-line` nie ma w bundlu** (`grep -c whitespace-pre-line
  assets/css/style.css` → 0), więc łamanie wierszy musi przyjść z `custom.css`.
- **Animacja pojawiania:** `data-reveal` siedzi na statycznym kontenerze `#lista-wydarzen`,
  nie na wpisach tworzonych przez JS. `initScrollReveal()` robi `qsa("[data-reveal]")`
  raz, na starcie — elementy dołożone później nie byłyby obserwowane. Kontener istnieje
  w HTML-u od początku (z `hidden`), więc trafia do obserwatora; gdy `initWydarzenia()`
  zdejmie `hidden`, obserwator go zauważy i nada `is-visible`. Dzięki temu
  `initScrollReveal()` zostaje nietknięty i kolejność wywołań nie ma znaczenia.
- Kolory wyłącznie przez zmienne motywu — sprawdzić we **wszystkich czterech** motywach.

## Configuration

| Zmienna | Domyślnie | Wartość produkcyjna |
|---|---|---|
| `WYDARZENIA_SCIEZKA` | `data/wydarzenia.json` w repo | `/opt/apps/app_winnicakielnagora.pl/dane/wydarzenia.json` |

Ścieżka produkcyjna jest analogiczna do `CENNIK_SCIEZKA` z TODO #26
(`/opt/apps/app_winnicakielnagora.pl/dane/wina.json`) — poza katalogiem wdrożenia, żeby
deploy nie kasował wpisów. Zmienną trzeba dopisać do konfiguracji `projects_manager` razem
z wdrożeniem, tak samo jak swego czasu `CENNIK_SCIEZKA`; katalog `dane/` już tam istnieje.

Panel działa tylko przy ustawionych `PANEL_UZYTKOWNIK` i `PANEL_HASLO_HASH` — bez zmian.

## Kryteria akceptacji

- Wpis z `data_od <= dzis <= data_do` jest widoczny na stronie głównej.
- Wpis z `dzis < data_od` oraz wpis z `dzis > data_do` **nie trafiają do przeglądarki** —
  nie ma ich w odpowiedzi `/data/wydarzenia.json`, nie tylko w renderze.
- Wydarzenie jednodniowe (`data_od == data_do`) jest widoczne w swoim dniu.
- Wpis z `data_publikacji_od` wcześniejszą niż `data_od` pokazuje się **przed** rozpoczęciem
  wydarzenia, a zakres dat na karcie dalej opisuje sam termin, nie datę publikacji.
- Wpis bez `data_publikacji_od` zachowuje się dokładnie jak przed tą zmianą — pliki sprzed
  niej nie wymagają migracji ani nie powodują błędu walidacji.
- `data_publikacji_od > data_do` → `400`; taki wpis nigdy nie byłby widoczny.
- Wpis ze `zdjecie` pokazuje je nad tytułem; wpis bez tego pola wygląda dokładnie jak dotąd.
- `zdjecie` wskazujące nieistniejący plik → `400`, plik nietknięty.
- Lista zdjęć w formularzu wydarzenia jest ta sama co w formularzu pozycji cennika.
- `aktywne()` przyjmuje `dzis` jako argument, więc granice da się sprawdzić testem bez
  czekania na kalendarz.
- Pusta lista albo same nieaktywne wpisy → sekcja `#wydarzenia` wygląda dokładnie jak dziś.
- Brak pliku albo błąd składni → sekcja jak dziś + `console.error`, bez komunikatu dla użytkownika.
- Panel pokazuje wszystkie wpisy, także nieaktywne, z czytelnym znacznikiem stanu.
- Klik w nagłówek sekcji Pozycje, Wydarzenia albo Kategorie chowa i pokazuje jej zawartość;
  `aria-expanded` odzwierciedla stan, a przyciski akcji w nagłówku dalej działają.
- Sekcje formularzy nie mają przełącznika zwijania.
- `data_do` wcześniejsza niż `data_od` → `400`, komunikat przy polu, plik nietknięty.
- Pusty tytuł, pusta treść, zła data, data nieistniejąca, zduplikowane `id` → błąd walidacji,
  plik nietknięty.
- Zapis wydarzeń nie zmienia `data/wina.json` i odwrotnie; niezapisane zmiany w obu sekcjach
  naraz wyzwalają ostrzeżenie `beforeunload`.
- Treść z `<script>` w środku wyświetla się jako tekst, nie wykonuje się.
- `wsgi.py` nie zawiera żadnego porównania dat — filtr jest w `wydarzenia.py` (GUARDRAILS #3).
- Sekcja czytelna we wszystkich czterech motywach i na telefonie.
- `/data/wydarzenia.json` ma `Cache-Control: no-store`.
- Wszystkie istniejące zestawy testów przechodzą (`.ai/GUARDRAILS.md` → „Definition of done").

## Implementation Checklist

- [x] Wstrzyknąć standardy: `content/wina-json`, `content/html-editing`,
  `frontend/js-conventions`, `frontend/theming`.
- [x] `data/wydarzenia.json` — pusta wersja startowa.
- [x] `wydarzenia.py` — odczyt, walidacja, zapis atomowy, kopia `.bak`,
  `dzis_w_winnicy()`, `aktywne()`.
- [x] `tools/test-wydarzenia.py` — odpowiednik `tools/test-cennik-sciezka.py`: zasiew pliku,
  `WYDARZENIA_SCIEZKA` poza projektem, kopia `.bak`, plus granice `aktywne()` przez
  wstrzyknięty `dzis`.
- [x] `wsgi.py` — trasa publiczna (bez logiki dat) + dwie akcje panelu.
- [x] `tools/panel/serwer.py` — `"/api/wydarzenia-wczytaj"` w `do_GET`,
  `"/api/wydarzenia-zapisz"` w krotce dozwolonych ścieżek `do_POST`.
- [x] `tools/panel/panel.html` — sekcja, lista, formularz; przeniesienie `#sciezka`
  i przycisków cennika ze sticky paska do nagłówka sekcji „Pozycje".
- [x] `tools/panel/panel.js` — nowy stan, nowe ID, wspólny `#komunikat`,
  rozszerzony `beforeunload`, `initZwijanieSekcji()`.
- [x] `tools/panel/panel.css` — style nowej sekcji oraz przełącznika zwijania.
- [x] `index.html` — kontener `#lista-wydarzen` w sekcji `#wydarzenia`.
- [x] `assets/css/custom.css` — `.wydarzenie-tresc { white-space: pre-line; }`.
- [x] `assets/js/main.js` — `initWydarzenia()` + rejestracja w `DOMContentLoaded`.
- [x] `tools/test-routing.py` — nowa trasa publiczna i jej nagłówki.
- [ ] `TODO.md` — dopisać `WYDARZENIA_SCIEZKA` do opisu wdrożenia obok `CENNIK_SCIEZKA`
  (dokument uzgadniany z Właścicielem — zmiana dopiero po jego zgodzie).
- [x] Przegląd w przeglądarce: cztery motywy, telefon, stany pusty / aktywny / błędny.

Rozszerzenie z 2026-09-03 (data publikacji + zdjęcie):

- [x] `wydarzenia.py` — pola opcjonalne, `aktywne()` liczy od daty publikacji, walidacja zdjęcia.
- [x] `tools/panel/panel.html` — pola „Widoczne od" i „Zdjęcie".
- [x] `tools/panel/panel.js` — obsługa obu pól, `<select>` z listy `zdjecia`, sekwencyjne wczytanie.
- [x] `assets/js/main.js` — render zdjęcia w karcie wydarzenia (układ dwukolumnowy).
- [x] `tools/test-wydarzenia.py` i `tools/test-routing.py` — granice publikacji, zgodność wstecz.
- [x] Przegląd w przeglądarce: wpis zapowiedziany, wpis ze zdjęciem, wpis bez zdjęcia.

## Implementation Review

Weryfikacja na obu wejściach panelu naraz: `tools/panel/serwer.py` (port 8765) i Flask
z `wsgi.py` (port 8007), oba ze `WYDARZENIA_SCIEZKA` wskazującą katalog poza repozytorium —
dzięki temu sprawdzona została też sama zmienna, a `data/wydarzenia.json` w repo pozostał pusty.

**Panel**

- Trzy wpisy dodane formularzem: aktywny, przyszły i zakończony. Znaczniki stanu policzone
  w przeglądarce zgodziły się z datami (`aktywne`, `przyszłe`, `zakończone`).
- Identyfikatory wygenerowane z polskich tytułów: `dzien-otwarty`, `winobranie-2026`,
  `zakonczone-spotkanie`.
- Zapis z `data_do` wcześniejszą niż `data_od` odrzucony przez serwer z komunikatem
  „wydarzenie 3: „data do” nie może być wcześniejsza niż „data od” (data_do)”.
  **Plik roboczy pozostał wtedy pusty** — walidacja jest przed zapisem.
- Po poprawieniu dat zapis się powiódł, powstała kopia `.bak`, `#stan-zmian` się wyczyścił,
  a stan cennika (`zmienione`) pozostał nietknięty — zapis jednej sekcji nie dotyka drugiej.
- Zwijanie: kliknięcie nagłówka „Pozycje” ustawiło `aria-expanded="false"` i schowało ciało
  sekcji; przełączniki istnieją dokładnie przy trzech sekcjach treściowych
  (Pozycje, Wydarzenia, Kategorie), a przyciski akcji w nagłówku działają dalej.

**Strona**

- `/data/wydarzenia.json` oddał **wyłącznie** wpis aktywny; `winobranie-2026`
  i `zakonczone-spotkanie` nie pojawiły się w treści odpowiedzi. Nagłówki: `no-store`,
  `application/json; charset=utf-8`.
- Sekcja `#wydarzenia` pokazała jedną kartę nad kartą degustacji, z zakresem
  „1 września – 30 września 2026” i zachowaną pustą linią w treści
  (`white-space` policzone jako `pre-line`, czyli reguła z `custom.css` działa).
- Cztery motywy: tło karty i kolor tytułu idą za tokenami motywu
  (`classic` #f6f5f3/#2e2e2e, `modern` #ffffff/#1a1a1a, `rustic` #f1ece4/#2e251f,
  `dark` #191b1f/#f3f1ed).
- Pusty plik → sekcja bez zmian. Uszkodzony JSON → trasa oddaje `500` z pustą listą,
  strona główna dalej `200`, kontener zostaje ukryty, karta degustacji nietknięta,
  a w konsoli ląduje `console.error` — odwiedzający nie widzi żadnego komunikatu o błędzie.

**Testy** — pięć zestawów przechodzi: `test-routing` (rozszerzony o trasę wydarzeń i o kontrolę,
że `wsgi.py` nie porównuje dat), `test-wydarzenia` (36 asercji), `test-cennik-sciezka`,
`test-panel-auth`, `test-serwowanie`.

**Znalezione i naprawione w trakcie**

- `proponujId()` w `panel.js` jest cennikowe — sięga do `cennik.wina` i `wybrany`. Użyte dla
  wydarzeń deduplikowałoby identyfikatory po ID win i wywalałoby się, gdyby wydarzenia
  wczytały się przed cennikiem. Wydzielone `slugWydarzenia()`.
- Długa ścieżka pliku w nagłówku sekcji wypychała stronę w poziomie. Nagłówek dostał
  `flex-wrap`, ścieżka `overflow-wrap: anywhere`.

**Znane, nienaprawione (poza zakresem)** — panel przewija się w poziomie przy szerokości
360 px przez spany `.kropka` w liście cennika. To istniejący markup, nie ta zmiana; panel
jest narzędziem desktopowym.

## Changelog

### 2026-09-03

- Pierwsza wersja specyfikacji wydarzeń redagowanych w panelu.
- Ustalono filtrowanie po stronie serwera i domknięte granice przedziału dat.
- Zapisano świadome ograniczenie: brak zapowiedzi wydarzeń przy czterech polach z zadania.
- Po recenzji `spec-reviewer`: filtr dat przeniesiony jednoznacznie do `wydarzenia.py`
  (GUARDRAILS #3 zabrania logiki biznesowej w `wsgi.py` poza panelem); rozpisana architektura
  panelu z dwiema sekcjami (stan, ID, wspólny komunikat, `beforeunload`); dosłowne ścieżki
  dla `serwer.py` i różnica modelu bezpieczeństwa obu wejść; konkretna ścieżka produkcyjna
  `WYDARZENIA_SCIEZKA`; dodany test odpowiadający `test-cennik-sciezka.py`; poprawiony
  fałszywy opis klas karty degustacji; `white-space: pre-line` przeniesione do `custom.css`,
  bo klasy `whitespace-pre-line` nie ma w bundlu; rozstrzygnięta animacja `data-reveal`
  i zasiew pliku na trasie publicznej.
- Po drugiej recenzji (PASS): dodane dwie brakujące decyzje UI — wspólny `#stan-zmian`
  w sticky pasku oraz pole `sciezka` w odpowiedzi `wydarzenia-wczytaj`, żeby nagłówek sekcji
  pokazywał realny plik roboczy. Potwierdzone bezpośrednim grepem: jedyna klasa `whitespace-*`
  w bundlu Tailwinda to `whitespace-nowrap`.
- Na wniosek Właściciela dodane zwijanie sekcji treściowych panelu (Pozycje, Wydarzenia,
  Kategorie) klikalnym nagłówkiem; sekcje formularzy zostają bez przełącznika.
- Na wniosek Właściciela zniesione dwa ograniczenia zapisane w pierwszej wersji: wpis dostaje
  opcjonalną `data_publikacji_od` (zapowiedź przed terminem; puste pole = zachowanie sprzed
  zmiany, bez migracji danych) oraz opcjonalne `zdjecie` — slug z tej samej biblioteki co
  pozycje cennika. Walidacja zdjęcia sprawdza istnienie pliku, więc `wydarzenia.py` nie
  importuje `cennik.py` ani nie powiela listy slugów.
- Walidacja odrzuca też slug z końcówką `-sm`: plik miniatury **istnieje**, więc sama kontrola
  obecności go przepuszczała, a karta dostałaby obraz 600 px. Wychwycił to test, nie przegląd.
- Wpis ze zdjęciem renderuje się w układzie dwukolumnowym zamiast paska nad tekstem —
  biblioteka zawiera kadry pionowe, które w proporcji 16:9 były przycinane do wąskiego wycinka.
- Wdrożone. Odstępstwo od specyfikacji: identyfikator wpisu nadaje `slugWydarzenia()`,
  a nie `proponujId()` — ta druga funkcja jest cennikowa i zależy od stanu cennika.
