# Hero zależny od pory dnia

## Overview

Hero strony głównej oraz tło strony 404 mają pokazywać jeden z czterech kadrów winnicy
zależnie od aktualnej godziny w strefie `Europe/Warsaw`. Zmiana dotyczy wyłącznie obrazu;
treść, CTA, gradient i wysokość obu widoków pozostają bez zmian.

Wariant `modern` jest pełnym ciemnym motywem. Przy automatycznym albo testowym wyborze
`noc.png` witryna aktywuje go bez nadpisywania stylu zapisanego przez użytkownika.

Źródła dostarczone przez Właściciela znajdują się w
`docs/materialy-do-wykorzystania/hero/`. `wsgi.py` dopuszcza publicznie tylko katalogi
z `KATALOGI_PUBLICZNE`, gdzie znajduje się `attached_assets`, ale nie `docs`. Dlatego do
`attached_assets/photos/hero/` trafią kopie dostarczonych PNG bez konwersji i utraty jakości.

## User Stories

### 1. Odwiedzający otwiera stronę rano lub w ciągu dnia

**Persona:** osoba planująca wizytę w winnicy, otwierająca stronę rano albo w przerwie
obiadowej. Oczekuje aktualnego, jasnego pierwszego wrażenia bez wykonywania dodatkowych akcji.

1. Użytkownik otwiera stronę główną.

   ```text
   ┌──────────────────────────────────────────────┐
   │  [ kadr winnicy właściwy dla godziny ]       │
   │                                              │
   │        Winnica Kielna Góra                   │
   │        Tradycyjne wina…                      │
   └──────────────────────────────────────────────┘
   ```

   **Za kulisami:** `initHeroImage()` pobiera godzinę dla `Europe/Warsaw`, wybiera
   `poranek` dla 06:00–11:59 albo `dzien` dla 12:00–17:59 i ustawia `src` elementu
   `#hero-image` na ścieżkę zapisaną w jego `dataset`.

   > **Zmiana vs. stan obecny:** obecnie hero zawsze pokazuje
   > `winnica-panorama-01.jpg`. Po zmianie obraz odpowiada porze dnia w Kielnarowej;
   > układ i tekst pozostają identyczne.

### 2. Odwiedzający ma stronę otwartą podczas zmiany przedziału

**Persona:** klient przeglądający ofertę wieczorem, który pozostawia kartę otwartą przez
dłuższy czas i wraca do początku strony po 22:00.

1. O 21:59 hero pokazuje zachód słońca.

   ```text
   21:59  ──►  zachod.png
   22:00  ──►  noc.png
   ```

2. Po przekroczeniu granicy przedziału obraz aktualizuje się bez przeładowania strony.

   **Za kulisami:** ta sama funkcja wyboru uruchamia się przy starcie i co 60 sekund.
   Jeżeli wybrany URL jest już ustawiony, DOM nie jest modyfikowany ponownie.

   > **Zmiana vs. stan obecny:** obecnie obraz nie reaguje na upływ czasu. Po zmianie
   > otwarta karta przechodzi do kolejnego kadru najpóźniej minutę po granicy przedziału.

### 3. Nocny kadr przełącza witrynę na ciemny motyw

**Persona:** odwiedzający otwierający stronę po 22:00. Chce czytelnego, spokojnego wizualnie
widoku, który pasuje do nocnej fotografii, bez ręcznego zmieniania ustawień.

1. Strona najpierw odczytuje zapisaną preferencję motywu, a następnie wybiera porę dnia.

   ```text
   zapisany motyw: classic     pora: noc
              └──────────────┬──────────────┘
                             ▼
                 noc.png + Modern Minimal Dark
   ```

2. Automatyczny wybór `modern` nie zapisuje się do `localStorage`. Ręczny wybór stylu
   pozostaje możliwy i jest zapisywany jak dotychczas.

3. Gdy otwarta karta przejdzie z nocy do poranka, przywracany jest ostatni styl wybrany
   przez użytkownika.

   **Za kulisami:** `setTheme(style, persist)` rozdziela zastosowanie palety od zapisu
   preferencji. `initHeroImage()` reaguje tylko na zmianę przedziału, dzięki czemu ręczny
   wybór dokonany już w nocy nie jest cofany przy każdej aktualizacji minutowej.

   > **Zmiana vs. stan obecny:** obecnie `modern` jest jasny, a wybór `noc.png` nie wpływa
   > na resztę interfejsu. Po zmianie noc uruchamia ciemną paletę, a poranek przywraca
   > zapisaną preferencję.

## Warianty czasowe

| Czas w `Europe/Warsaw` | Klucz | Plik publiczny |
|---|---|---|
| 06:00–11:59 | `poranek` | `attached_assets/photos/hero/poranek.png` |
| 12:00–17:59 | `dzien` | `attached_assets/photos/hero/dzien.png` |
| 18:00–21:59 | `zachod` | `attached_assets/photos/hero/zachod.png` |
| 22:00–05:59 | `noc` | `attached_assets/photos/hero/noc.png` |

Granice są domknięte od początku i otwarte od końca. Przykładowo dokładnie 12:00 oznacza
`dzien`, a dokładnie 22:00 — `noc`.

## Architecture

- `index.html`: istniejący obraz hero otrzyma `id="hero-image"`, cztery atrybuty `data-*`
  ze ścieżkami oraz `data-fallback-src` wskazujący dotychczasową panoramę. Element nie ma
  początkowego `src`, więc przeglądarka nie pobiera błędnego kadru przed wykonaniem JS.
  W `<noscript>` pozostaje dzienny obraz awaryjny dla przeglądarek bez JavaScriptu.
- `404.html`: obraz tła otrzyma tę samą konfigurację `#hero-image` i `<noscript>`, dzięki
  czemu korzysta z jednej implementacji w `main.js`, również pod głęboko zagnieżdżonym
  nieistniejącym adresem.
- `assets/js/main.js`: czysta funkcja `heroPeriodForHour(hour)` mapuje liczbę 0–23 na klucz
  obrazu. Nowa funkcja `initHeroImage()` zgodna ze wzorcem `initX()` ustawia obraz i jest
  rejestrowana w istniejącym `DOMContentLoaded`.
- `themeStyles.modern`: zachowuje ten sam komplet 29 zmiennych co pozostałe motywy, ale
  otrzymuje ciemną paletę grafitową z ciepłym akcentem. Każdy motyw deklaruje także
  `colorScheme` (`dark` dla `modern`, `light` dla `classic` i `rustic`) dla natywnych kontrolek.
- `setTheme(style, persist = true)`: automatyczne przełączenie wywołuje funkcję z `false`,
  a ręczny wybór zachowuje domyślny zapis do `localStorage["winery-style"]`. Poza pętlą
  29 zmiennych funkcja ustawia `document.documentElement.style.colorScheme` z konfiguracji
  motywu i wywołuje `updateStyleMenu(style)`, więc menu zawsze wskazuje styl faktycznie widoczny.
- Kolejność startowa: `initStyleSwitcher()` przed `initHeroImage()`. Najpierw ładowana jest
  preferencja, potem noc może tymczasowo zastosować `modern`.
- Czas: `Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Warsaw", hour: "numeric",
  hourCycle: "h23" })` i `formatToParts()` zapewniają zakres 00–23, również o północy.
  Wynik spoza zakresu albo błąd `Intl` powoduje użycie lokalnej godziny urządzenia.
- Aktualizacja obrazu: interwał 60 sekund, bez żądań API i bez nowego stanu trwałego. Mechanizm
  może odczytać istniejący `localStorage["winery-style"]`, ale zapisuje go wyłącznie ręczny
  wybór użytkownika; automatyczne wejście w noc nigdy go nie zmienia.
- Błąd obrazu: `initHeroImage()` przechowuje w swoim domknięciu URL, którego pobranie nie
  powiodło się. Handler `error` ustawia dotychczasową panoramę, ale nie oznacza jej jako
  wariantu czasowego. Aktualizacje minutowe nie ponawiają uszkodzonego URL-a w tym samym
  przedziale. Po zmianie pory nowy URL może zostać pobrany normalnie. Błąd samej panoramy
  awaryjnej nie powoduje kolejnej podmiany, więc nie powstaje pętla.
- Obrazy: źródłowe PNG są kopiowane bez zmian (1534×1025). Identyczne proporcje zapobiegają
  zmianie kadru i layout shift.

## Data Models

Brak modelu danych. Mapowanie pory dnia na URL jest zapisane w `data-*` elementu hero,
a bieżący wybór żyje wyłącznie w DOM.

## API Contracts

Brak nowych endpointów i żądań sieciowych poza pobraniem wybranego pliku obrazu.

## UI/UX

- Zachowane zostają klasy sekcji `.relative h-[600px] md:h-[700px] w-full overflow-hidden`.
- `object-cover`, gradient, treść i CTA pozostają bez zmian.
- Obraz nadal jest dekoracyjny (`alt=""`).
- Przed wyborem nie jest pobierany żaden sieciowy obraz hero, dlatego start nie pokazuje
  niewłaściwej pory i nie wykonuje podwójnego pobrania. Po wyborze zmienia się tylko `src`.
- Funkcja ma działać jednakowo na desktopie, telefonie i we wszystkich trzech motywach.
- Ciemny `modern` musi zachować czytelność tekstu, kart, filtrów, formularza, menu i koszyka;
  wszystkie kolory nadal pochodzą wyłącznie ze zmiennych motywu.

## Configuration

Stała strefa czasowa: `Europe/Warsaw`. To świadoma decyzja produktu: obraz przedstawia
aktualną porę w winnicy, więc wszyscy odwiedzający widzą ten sam kadr niezależnie od swojej
lokalizacji. Brak zmiennych środowiskowych i flag funkcji.

Automatyczny `modern` jest stanem prezentacji, nie preferencją. Jedynym trwałym ustawieniem
pozostaje ręczny wybór w `localStorage["winery-style"]`. Brak wpisu albo wartość spoza
`classic`, `modern`, `rustic` oznacza domyślny `classic`.

## Kryteria akceptacji

- Każdy z czterech przedziałów wskazuje dokładnie przypisany obraz.
- Godziny graniczne 06:00, 12:00, 18:00 i 22:00 wybierają prawidłowy wariant.
- `heroPeriodForHour()` umożliwia sprawdzenie wszystkich przedziałów i granic bez czekania
  na rzeczywistą godzinę.
- Otwarta strona aktualizuje obraz po zmianie przedziału bez przeładowania.
- Brakujący element hero nie powoduje błędu JavaScript.
- Niedostępny wariant czasowy powoduje użycie dotychczasowej panoramy zamiast uszkodzonego obrazu.
- Publiczne obrazy są dostępne przez routing produkcyjny.
- Strona 404 wybiera ten sam wariant czasowy co strona główna i zachowuje kod HTTP 404.
- Widok zachowuje czytelność na desktopie i telefonie we wszystkich motywach.
- `modern` ma pełną ciemną paletę i `color-scheme: dark`; dwa pozostałe motywy pozostają jasne.
- `noc.png` automatycznie aktywuje `modern` na stronie głównej i 404 bez zmiany zapisanej preferencji.
- Przejście z nocy do poranka przywraca ręcznie zapisaną preferencję.
- Ręczna zmiana stylu po automatycznym wyborze nocnym nie jest cofana co minutę.

## Implementation Checklist

- [x] Wstrzyknąć standardy `frontend/js-conventions` i `content/html-editing`.
- [x] Skopiować cztery źródłowe PNG do `attached_assets/photos/hero/`.
- [x] Dodać konfigurację wariantów i fallback do obrazu hero w `index.html`.
- [x] Dodać `heroPeriodForHour()` i `initHeroImage()` w `assets/js/main.js`.
- [x] Podłączyć ten sam mechanizm do obrazu tła w `404.html`.
- [x] Sprawdzić granice czasowe, routing obrazów, standardy i widok w przeglądarce.
- [x] Wstrzyknąć standardy dla rozszerzenia: `frontend/theming`, `frontend/js-conventions`
  i `frontend/styling`.
- [x] Zmienić `themeStyles.modern` na pełną ciemną paletę z `colorScheme: "dark"`.
- [x] Powiązać wejście i wyjście z okresu `noc` z tymczasowym motywem `modern`.
- [x] Zweryfikować nocny motyw na stronie głównej i 404 oraz przywracanie preferencji.

## Implementation Review

- Sprawdzono mapowanie wszystkich 24 godzin oraz wartości spoza zakresu.
- Sprawdzono fallback uszkodzonego obrazu i przejście do kolejnego przedziału.
- Cztery PNG są bitowo identyczne z materiałami źródłowymi i zwracają HTTP 200.
- Chrome wybrał `noc.png` zgodnie z aktualną godziną `Europe/Warsaw`.
- Strona 404 pod nieistniejącym adresem zachowuje kod 404 i wybiera ten sam obraz czasowy.
- Widok hero sprawdzono w Chrome na desktopie 1440×900, telefonie 390×844 oraz we
  wszystkich trzech motywach: `classic`, `modern` i `rustic`.
- Kod jest zgodny z `frontend/js-conventions` i zaktualizowanym `content/html-editing`.
- Ciemny `modern` sprawdzono w Chrome na stronie głównej, w sklepie i na stronie 404,
  również w widoku telefonu 390×844; karty, filtry, menu i formularz pozostają czytelne.
- Potwierdzono, że noc automatycznie wybiera `modern` bez zapisu do `localStorage`, ręczny
  wybór pozostaje trwały, a poranek przywraca zapisaną preferencję.
- Nakładka strony 404 korzysta z koloru `--primary`, dzięki czemu nie rozjaśnia nocnego
  zdjęcia i zachowuje kontrast we wszystkich trzech motywach.

## Changelog

### 2026-09-03

- Pierwsza wersja specyfikacji czasowego obrazu hero.
- Wdrożono cztery warianty czasowe, obsługę fallbacku i automatyczną aktualizację.
- Rozszerzono wybór czasowy na stronę 404 bez duplikowania logiki JavaScript.
- Doprecyzowano wymagania dla ciemnego wariantu `modern` aktywowanego przez nocny kadr.
- Wdrożono ciemną paletę `modern`, automatyczne przełączanie nocne i przywracanie preferencji.
