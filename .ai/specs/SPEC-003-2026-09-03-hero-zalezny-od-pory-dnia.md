# Hero zależny od pory dnia

## Overview

Hero strony głównej oraz tło strony 404 mają pokazywać jeden z czterech kadrów winnicy
zależnie od aktualnej godziny w strefie `Europe/Warsaw`. Zmiana dotyczy wyłącznie obrazu;
treść, CTA, gradient i wysokość obu widoków pozostają bez zmian.

Wariant `modern` jest pełnym ciemnym motywem. Przy automatycznym albo testowym wyborze
pory `noc` witryna aktywuje go bez nadpisywania stylu zapisanego przez użytkownika —
na stronie głównej, na stronie 404 **i na podstronach odmian**, które nie mają hero.

Źródła dostarczone przez Właściciela znajdują się w
`docs/materialy-do-wykorzystania/hero/`. `wsgi.py` dopuszcza publicznie tylko katalogi
z `KATALOGI_PUBLICZNE`, gdzie znajduje się `attached_assets`, ale nie `docs`. Dlatego do
`attached_assets/photos/hero/` trafiają **wyłącznie pliki WebP** wygenerowane z tych PNG
przez `tools/optimize-hero.py`: kadr hero jest elementem LCP, a PNG po ok. 2 MB kasował cały
zysk z wczesnego wykrycia obrazu. Mastery PNG zostają poza repozytorium, w katalogu źródłowym
— tak samo jak materiał dla `tools/optimize-photos.py`. Świeży klon nie odtworzy kadrów
bez oryginałów od Właściciela; to świadoma decyzja, repozytorium nie magazynuje źródeł. Operacyjny opis ról plików,
decyzji o przechowywaniu masterów i podmiany kadru znajduje się obok grafik w
`attached_assets/photos/hero/README.md`.

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

   > **Zmiana vs. stan przed wdrożeniem:** hero zawsze pokazywało
   > `winnica-panorama-01.jpg`. Po zmianie obraz odpowiada porze dnia w Kielnarowej;
   > układ i tekst pozostają identyczne.

### 2. Odwiedzający ma stronę otwartą podczas zmiany przedziału

**Persona:** klient przeglądający ofertę wieczorem, który pozostawia kartę otwartą przez
dłuższy czas i wraca do początku strony po 22:00.

1. O 21:59 hero pokazuje zachód słońca.

   ```text
   21:59  ──►  zachod.webp
   22:00  ──►  noc.webp
   ```

2. Po przekroczeniu granicy przedziału obraz aktualizuje się bez przeładowania strony.

   **Za kulisami:** ta sama funkcja wyboru uruchamia się przy starcie i co 60 sekund.
   Jeżeli wybrany URL jest już ustawiony, DOM nie jest modyfikowany ponownie.

   > **Zmiana vs. stan przed wdrożeniem:** obraz nie reagował na upływ czasu. Po zmianie
   > otwarta karta przechodzi do kolejnego kadru najpóźniej minutę po granicy przedziału.

### 3. Nocny kadr przełącza witrynę na ciemny motyw

**Persona:** odwiedzający otwierający stronę po 22:00. Chce czytelnego, spokojnego wizualnie
widoku, który pasuje do nocnej fotografii, bez ręcznego zmieniania ustawień.

1. Strona najpierw odczytuje zapisaną preferencję motywu, a następnie wybiera porę dnia.

   ```text
   zapisany motyw: classic     pora: noc
              └──────────────┬──────────────┘
                             ▼
                 noc.webp + Modern Minimal Dark
   ```

2. Automatyczny wybór `modern` nie zapisuje się do `localStorage`. Ręczny wybór stylu
   pozostaje możliwy i jest zapisywany jak dotychczas.

3. Gdy otwarta karta przejdzie z nocy do poranka, przywracany jest ostatni styl wybrany
   przez użytkownika.

   **Za kulisami:** `setTheme(style, persist)` rozdziela zastosowanie palety od zapisu
   preferencji. `initHeroImage()` reaguje tylko na zmianę przedziału, dzięki czemu ręczny
   wybór dokonany już w nocy nie jest cofany przy każdej aktualizacji minutowej.

   > **Zmiana vs. stan przed wdrożeniem:** `modern` był jasny, a wybór pory `noc` nie wpływał
   > na resztę interfejsu. Po zmianie noc uruchamia ciemną paletę, a poranek przywraca
   > zapisaną preferencję.

## Warianty czasowe

| Czas w `Europe/Warsaw` | Klucz | Plik publiczny |
|---|---|---|
| 06:00–11:59 | `poranek` | `attached_assets/photos/hero/poranek.webp` |
| 12:00–17:59 | `dzien` | `attached_assets/photos/hero/dzien.webp` |
| 18:00–21:59 | `zachod` | `attached_assets/photos/hero/zachod.webp` |
| 22:00–05:59 | `noc` | `attached_assets/photos/hero/noc.webp` |

Granice są domknięte od początku i otwarte od końca. Przykładowo dokładnie 12:00 oznacza
`dzien`, a dokładnie 22:00 — `noc`.

## Architecture

- `index.html`: obraz hero ma `id="hero-image"`, cztery atrybuty `data-*` ze ścieżkami
  oraz `data-fallback-src` wskazujący dotychczasową panoramę. W statycznym pliku nie ma
  `src` ani gotowego `<link rel="preload">` — jest tylko znacznik `<!-- hero-preload -->`,
  w który serwer wstawia preload właściwego kadru. W `<noscript>` pozostaje dzienny obraz
  awaryjny dla przeglądarek bez JavaScriptu.
- `wsgi.py`: dla adresu `/` **serwer** wybiera kadr według pory dnia w `Europe/Warsaw`
  (`_pora_hero_teraz()`) i wstawia jednocześnie `src` na `<img>` oraz `<link rel="preload">`
  na ten sam plik (`_wstrzyknij_hero`). Bez tego preload scanner nie ma czego znaleźć:
  nie zagląda do atrybutów `data-*-src`, więc obraz LCP odkrywałby dopiero odroczony
  `main.js` — a każdy preload wskazujący inny plik to dodatkowe, bezużyteczne pobranie.
  Gdy kotwica przestanie pasować, `_wstrzyknij_hero` zwraca `None`: strona główna oddaje
  wtedy plik bez zmian (działa, tylko wolniej), a narzędzie `?hero=` kończy się błędem 500,
  bo cichy pomiar na niepodmienionej stronie prowadzi do fałszywych wniosków.
  `_pora_hero()` powiela siatkę godzin z `heroPeriodForHour()` — nie ma kroku budowania,
  który podałby jedną definicję obu stronom, więc granic pilnuje `tools/test-routing.py`.
- `404.html`: obraz tła otrzyma tę samą konfigurację `#hero-image` i `<noscript>`, dzięki
  czemu korzysta z jednej implementacji w `main.js`, również pod głęboko zagnieżdżonym
  nieistniejącym adresem.
- `assets/js/main.js`: czysta funkcja `heroPeriodForHour(hour)` mapuje liczbę 0–23 na klucz
  obrazu. `initHeroImage()` odpowiada wyłącznie za obraz i kończy się od razu, gdy na stronie
  nie ma `#hero-image`. Motyw przełącza osobne `initTimeTheme()` — **celowo niezależne od
  obrazu**, bo podstrony odmian (`wina/*.html`) ładują ten sam skrypt, ale hero nie mają;
  logika wpięta w inicjalizator obrazu nigdy się tam nie wykonywała i po zmroku strona główna
  była ciemna, a każda podstrona jasna. Obie funkcje są rejestrowane w `DOMContentLoaded`.
- `themeStyles.modern`: zachowuje ten sam komplet 29 zmiennych co pozostałe motywy, ale
  otrzymuje ciemną paletę grafitową z ciepłym akcentem. Każdy motyw deklaruje także
  `colorScheme` (`dark` dla `modern`, `light` dla `classic` i `rustic`) dla natywnych kontrolek.
- `setTheme(style, persist = true)`: automatyczne przełączenie wywołuje funkcję z `false`,
  a ręczny wybór zachowuje domyślny zapis do `localStorage["winery-style"]`. Poza pętlą
  29 zmiennych funkcja ustawia `document.documentElement.style.colorScheme` z konfiguracji
  motywu i wywołuje `updateStyleMenu(style)`, więc menu zawsze wskazuje styl faktycznie widoczny.
- Kolejność startowa: `initStyleSwitcher()` → `initTimeTheme()` → `initHeroImage()`.
  Najpierw ładowana jest preferencja, potem noc może tymczasowo zastosować `modern`.
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
- Obrazy: wszystkie cztery kadry mają 1534×1025, co zapobiega zmianie kadru i layout shift.
  Do przeglądarki idzie WebP q80 z `tools/optimize-hero.py` (2,0–2,3 MB PNG → 94–174 kB),
  generowany z masterów w `docs/materialy-do-wykorzystania/hero/` (poza repozytorium). Przeglądarki bez obsługi WebP obsługuje istniejąca ścieżka
  `data-fallback-src` — handler `error` podstawia `winnica-panorama-01.jpg`.

## Data Models

Brak modelu danych. Mapowanie pory dnia na URL jest zapisane w `data-*` elementu hero,
a bieżący wybór żyje wyłącznie w DOM.

## API Contracts

Brak nowych endpointów. Adres `/` przestał być jednak zwykłym plikiem statycznym: jego
treść zależy od pory dnia, więc `wsgi.py` składa odpowiedź sam i dokłada `ETag`
oraz `Cache-Control: no-cache` — dokładnie to, co wcześniej ustawiał `send_from_directory`.
Powrót na stronę to zwykle warunkowe żądanie i `304` bez ciała. Poza tym jedyne żądanie
sieciowe to pobranie wybranego pliku obrazu.

## UI/UX

- Zachowane zostają klasy sekcji `.relative h-[600px] md:h-[700px] w-full overflow-hidden`.
- `object-cover`, gradient, treść i CTA pozostają bez zmian.
- Obraz nadal jest dekoracyjny (`alt=""`).
- Dla zwykłego `/` serwer wybiera obraz przed wysłaniem HTML i wstawia ten sam URL do
  `preload` oraz `src`, dlatego preload scanner odkrywa właściwy kadr i przeglądarka pobiera
  tylko jeden obraz hero. JavaScript zmienia `src` dopiero po przekroczeniu granicy przedziału
  albo przy uruchomieniu kontrolowanego fallbacku.
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
- Pora `noc` automatycznie aktywuje `modern` na stronie głównej, 404 i podstronach odmian
  bez zmiany zapisanej preferencji.
- Przejście z nocy do poranka przywraca ręcznie zapisaną preferencję.
- Ręczna zmiana stylu po automatycznym wyborze nocnym nie jest cofana co minutę.
- Nocny motyw działa też na podstronach odmian (`wina/*.html`), które nie mają hero.
- Zwykłe wejście na `/` pobiera dokładnie jeden plik hero: ten, który zostanie wyświetlony.
  Żaden kadr ani obraz zapasowy nie jest pobierany „na zapas".
- `<link rel="preload">` na stronie głównej wskazuje ten sam plik co `src` elementu hero,
  więc preload scanner znajduje obraz LCP bez czekania na `main.js`.
- Wynik pomiaru z `?hero=` odpowiada temu, co dostaje zwykły odwiedzający na `/`.
- Kadr hero waży poniżej 200 kB.

## Implementation Checklist

- [x] Wstrzyknąć standardy `frontend/js-conventions` i `content/html-editing`.
- [x] ~~Skopiować cztery źródłowe PNG do `attached_assets/photos/hero/`.~~ Zastąpione:
  do repozytorium trafiają tylko WebP, mastery zostają w katalogu źródłowym.
- [x] Dodać konfigurację wariantów i fallback do obrazu hero w `index.html`.
- [x] Dodać `heroPeriodForHour()` i `initHeroImage()` w `assets/js/main.js`.
- [x] Podłączyć ten sam mechanizm do obrazu tła w `404.html`.
- [x] Sprawdzić granice czasowe, routing obrazów, standardy i widok w przeglądarce.
- [x] Wstrzyknąć standardy dla rozszerzenia: `frontend/theming`, `frontend/js-conventions`
  i `frontend/styling`.
- [x] Zmienić `themeStyles.modern` na pełną ciemną paletę z `colorScheme: "dark"`.
- [x] Powiązać wejście i wyjście z okresu `noc` z tymczasowym motywem `modern`.
- [x] Zweryfikować nocny motyw na stronie głównej i 404 oraz przywracanie preferencji.
- [x] Wydzielić `initTimeTheme()` z `initHeroImage()`, żeby noc obejmowała podstrony odmian.
- [x] Przekodować kadry na WebP (`tools/optimize-hero.py`) i przepiąć ścieżki w
  `index.html` oraz `404.html`.
- [x] Przenieść wybór kadru dla `/` na serwer wraz z `preload` (`wsgi.py`).
- [x] Dopisać testy pory dnia, podmiany hero i kotwic do `tools/test-routing.py`.
- [x] Usunąć mastery PNG z repozytorium i przepiąć `tools/optimize-hero.py` na katalog źródłowy.

## Implementation Review

- Sprawdzono mapowanie wszystkich 24 godzin oraz wartości spoza zakresu.
- Sprawdzono fallback uszkodzonego obrazu i przejście do kolejnego przedziału.
- Cztery PNG są bitowo identyczne z materiałami źródłowymi i zwracają HTTP 200.
- Chrome wybrał `noc.webp` zgodnie z aktualną godziną `Europe/Warsaw`.
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

Po przeglądzie kodu (Flask z venv, Chrome):

- Zwykłe `/` o 12:02 CEST: `preload` i `src` wskazują `dzien.webp`; jedyne pobranie hero to
  ten plik, 175 kB w 27 ms, inicjator `link`. `winnica-panorama-01.jpg` nie jest pobierany.
- `/wina/monarch.html?hero=noc`: strona ciemna mimo braku `#hero-image` — to właśnie
  przypadek, który wcześniej nie działał.
- Ręczny wybór `rustic` w trakcie nocy przetrwał tyknięcie zegara (102 s od załadowania)
  i został zapisany w `localStorage`.
- Trzy motywy sprawdzone na `/`: `classic` i `rustic` jasne, `modern` ciemny z
  `color-scheme: dark`; hero czytelne w każdym.
- Strona 404 pod nieistniejącym adresem: kod 404, kadr `dzien.webp`.
- `?hero=noc` podmienia kadr i pokazuje pasek; wartość spoza listy nie podmienia niczego.
- `304` na warunkowe żądanie `/`, gzip i `Vary: Accept-Encoding` bez zmian.
- Konsola bez błędów. Sklep renderuje 8 kart z cenami, filtry na miejscu (nietknięte).
- Cztery zestawy testów przechodzą: `test-routing`, `test-cennik-sciezka`,
  `test-panel-auth` (atrapa Flaska) oraz `test-serwowanie` (prawdziwy Flask).

## Changelog

### 2026-09-03 (poprawki po przeglądzie kodu)

- `initTimeTheme()` wydzielone z `initHeroImage()`. Wcześniej nocny ciemny motyw nigdy nie
  włączał się na ośmiu podstronach odmian, bo inicjalizator kończył się na braku
  `#hero-image`; odwiedzający po zmroku widział ciemną stronę główną i jasną podstronę.
- Wybór kadru hero dla `/` przeniesiony na serwer razem z `<link rel="preload">`.
  Wcześniej `/` preloadowało `winnica-panorama-01.jpg` (247 563 B), którego nigdy nie
  pokazywano, a właściwy kadr odkrywał dopiero odroczony `main.js`. Zapis o braku
  podwójnego pobierania dotyczył wyłącznie adresów `?hero=` i nie odpowiadał produkcji.
- Kadry przekodowane na WebP q80 (`tools/optimize-hero.py`): 2,0–2,3 MB PNG → 94–174 kB.
  PNG zostają w repozytorium jako master.
- `_wstrzyknij_hero` sprawdza, czy kotwica pasuje dokładnie raz. Wcześniej `str.replace`
  bez trafienia po cichu oddawał stronę bez podmiany — przy `?hero=` dawało to pomiar
  wyglądający na poprawny, ale zrobiony na niewłaściwym obrazie.
- `tools/test-routing.py`: siatka godzin, podmiana `src` i `preload` na `/`, warianty
  `?hero=` (w tym wartość spoza listy) oraz zachowanie przy niepasującej kotwicy.
- Mastery PNG (8,2 MB) usunięte z repozytorium — jechały na wdrożenie, choć żadna strona
  ich nie wczytywała. `tools/optimize-hero.py` czyta je teraz z katalogu źródłowego poza
  repozytorium. Sprawdzone: WebP odtworzone z masterów są bitowo identyczne z tymi w repo.

### 2026-09-03

- Pierwsza wersja specyfikacji czasowego obrazu hero.
- Wdrożono cztery warianty czasowe, obsługę fallbacku i automatyczną aktualizację.
- Rozszerzono wybór czasowy na stronę 404 bez duplikowania logiki JavaScript.
- Doprecyzowano wymagania dla ciemnego wariantu `modern` aktywowanego przez nocny kadr.
- Wdrożono ciemną paletę `modern`, automatyczne przełączanie nocne i przywracanie preferencji.
