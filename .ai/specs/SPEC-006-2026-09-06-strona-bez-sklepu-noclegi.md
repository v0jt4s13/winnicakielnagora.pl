# Strona bez sklepu online, bez degustacji, z noclegami

## Overview

Właściciel koryguje ofertę winnicy na start:

- **Sprzedaż online nie rusza** (brak logistyki, pudełek, wysyłki). Sekcja `#sklep`
  i koszyk mają **zniknąć z widoku**, ale kod, dane (`data/wina.json`) i panel cennika
  zostają w repozytorium gotowe do przywrócenia.
- **Degustacji nie oferujemy** (na razie). Wszystkie wzmianki o degustacjach schodzą z treści.
- **Wydarzenia zostają** — redagowane z panelu (SPEC-005, bez zmian). Statyczna karta
  „Degustacje po umówieniu" w sekcji `#wydarzenia` zostaje zastąpiona kartą opisującą
  **typy** wydarzeń: wyprzedaże roczników, pikniki, spotkania przy zbiorach.
- **Noclegi** — winnica wystawia 3 pokoje na Booking.com. Powstaje nowa sekcja `#noclegi`
  z zajawką i przyciskiem „Zarezerwuj na Booking". Realny link rezerwacyjny i zdjęcia
  pokoi Właściciel prześle później — teraz przycisk jest **nieaktywnym placeholderem**.

Powiązana, osobna zmiana: **przełącznik słowa „tradycyjne"** (`?slowo=`) na wzór `?hero=` —
opisana w `.ai/specs/quick/004-przelacznik-slowa-tradycyjne.md`, nie w tej specyfikacji.

Finalne brzmienie tekstów (m.in. „z bieszczadzkich stoków" w hero — winnica leży pod
Rzeszowem, nie w Bieszczadach) Właściciel poprawi sam po wdrożeniu szkieletu. Spec podaje
treści robocze i zaznacza, które pola czekają na jego wersję.

### Czego ta zmiana świadomie nie robi

- **Nie usuwa kodu sklepu.** Sekcja, koszyk, filtry, `renderSklep()`, `initCart()`,
  `assets/js/produkty.js`, `data/wina.json` i panel cennika zostają nietknięte co do logiki —
  zmienia się tylko to, czy sklep jest **renderowany i widoczny**. Powód: sprzedaż online
  ma wrócić, gdy winnica ogarnie wysyłkę. Ponowne włączenie to zmiana jednej flagi
  plus przywrócenie wpisów nawigacji.
- **Nie rusza SPEC-005** (wydarzenia w panelu). Trasa `/data/wydarzenia.json`, moduł
  `wydarzenia.py`, akcje panelu i `initWydarzenia()` działają bez zmian. Zmienia się
  wyłącznie statyczny markup karty pod listą wpisów.
- **Nie dodaje integracji z Booking.** Sekcja `#noclegi` to treść + link wychodzący.
  Żadnego API, żadnego pobierania dostępności — to byłoby zadanie rozmiaru L.
- **Nie wymyśla adresu rezerwacji.** Dopóki Właściciel nie poda linku, przycisk
  „Zarezerwuj na Booking" jest wizualnie obecny, ale nieklikalny, z podpisem
  „Rezerwacja wkrótce".

## User Stories

### 1. Odwiedzający szuka informacji o winnicy i możliwości noclegu

**Persona:** Marta — planuje weekend w okolicach Rzeszowa, szuka miejsca z klimatem.
Nie zna się na technologii, wchodzi z telefonu, przegląda stronę od góry do dołu.

1. Otwiera stronę główną. W nagłówku widzi krótsze menu:

   ```text
   ┌───────────────────────────────────────────────────────────────┐
   │ Winnica Kielna Góra   O Nas  Nasze Wina  Wydarzenia  Noclegi  │
   │                                                   Kontakt  ☰  │
   └───────────────────────────────────────────────────────────────┘
   ```

   > **Zmiana vs. stan obecny:** dziś menu ma sześć pozycji:
   > `O Nas · Nasze Wina · Sklep · Degustacje · Wydarzenia · Kontakt` (desktop w ~w. 138–143,
   > mobile ~w. 194–199). Po zmianie zostają cztery: **Sklep** i **Degustacje** znikają,
   > dochodzi **Noclegi** przed „Kontakt". Ikona koszyka w nagłówku (`#cart-button`,
   > ~w. 182) też znika (`hidden`).

2. W sekcji hero widzi zdjęcie i jedno wezwanie do działania:

   ```text
   ┌───────────────────────────────────────────────┐
   │            Winnica Kielna Góra                 │
   │        Tradycyjne wina z … stoków              │
   │        [ Poznaj nasze wina ]                   │
   └───────────────────────────────────────────────┘
   ```

   **Za kulisami:** przyciski hero to zwykłe `data-scroll` obsługiwane przez
   `initNavigation()` w `main.js` — brak elementu docelowego = klik nic nie robi
   (`if (el)` już jest).

   > **Zmiana vs. stan obecny:** dziś hero ma dwa przyciski: „Przejdź do sklepu"
   > (`data-scroll="#sklep"`) i „Degustacje" (`data-scroll="#degustacje"`, ~w. 218–219).
   > Po zmianie jeden przycisk „Poznaj nasze wina" → `data-scroll="#nasze-wina"`.
   > Tekst „Tradycyjne wina z bieszczadzkich stoków" zostaje bez zmian w tym zadaniu —
   > poprawi go Właściciel (i/lub przełącznik `?slowo=` z quick-spec 004).

3. Przewija do sekcji **Noclegi** (nowa, między „Wydarzenia" a „Kontakt"):

   ```text
   ┌───────────────────────────────────────────────┐
   │             Nocleg w winnicy                   │
   │   Trzy pokoje w budynku winiarni, z widokiem  │
   │   na winorośl. Rezerwacja przez Booking.com.  │
   │                                               │
   │        ( Zarezerwuj na Booking )               │
   │        Rezerwacja wkrótce                      │
   └───────────────────────────────────────────────┘
   ```

   **Za kulisami:** sekcja jest w całości statyczna w `index.html`, **bez zdjęć na start**
   (brak kadrów pokoi w zasobach — patrz Architecture → „Sekcja `#noclegi`"). Przycisk to
   `<a>` wizualnie wyszarzony z `aria-disabled="true"`, `href="#noclegi"` (kotwica do samej
   siebie, nie przewija). Zero JavaScriptu.

   > **Zmiana vs. stan obecny:** sekcji `#noclegi` dziś nie ma. To nowy blok treści.

4. Wraca na stronę po tygodniu — Właściciel podmienił link. Przycisk „Zarezerwuj na
   Booking" jest teraz aktywny i otwiera ofertę winnicy na Booking.com w nowej karcie.

   **Za kulisami:** osobne, małe zadanie (poza tą specyfikacją): podmiana `href`,
   zdjęcie `alt`-y, usunięcie `aria-disabled` i podpisu „Rezerwacja wkrótce".

### 2. Odwiedzający chce kupić wino

**Persona:** Tomasz — był na pikniku w winnicy, chce zamówić skrzynkę. Szuka na stronie
przycisku „kup".

1. Wchodzi, klika „Nasze Wina", trafia do sekcji `#nasze-wina` (bez zmian) i dalej na
   podstronę odmiany, np. `wina/dornfelder.html`.

   ```text
   ┌───────────────────────────────────────────────┐
   │  Wina z tej odmiany                            │
   │  Napisz do nas po aktualną dostępność.         │
   └───────────────────────────────────────────────┘
   ```

   **Za kulisami:** `initWineOffer()` w `main.js` renderuje pozycje z `data/wina.json`
   pasujące do `data-odmiana`. Gdy cennik ma pozycje z tej odmiany, pokazuje ich nazwy
   i ceny; gdy nie ma — zostaje tekst zastępczy z HTML-a.

   > **Zmiana vs. stan obecny:** dziś tekst zastępczy brzmi „Sprawdź aktualną dostępność
   > **w naszym sklepie**" i linkuje do `../index.html#sklep` (`wina/*.html`, ~w. 100–101,
   > w każdym z 8 plików). Przycisk renderowany przez `initWineOffer()` to „**Zobacz
   > w sklepie**" → `index.html#sklep` (`main.js` ~w. 777). Po zmianie: tekst i przycisk
   > kierują do **`#kontakt`** i mówią „Napisz do nas". Ceny (gdy cennik ma pozycje)
   > pokazują się dalej — to nadal jasna informacja handlowa, tylko bez koszyka.

2. Na podstronie w nagłówku widzi „Nasze odmiany" — bez linku „Sklep".

   > **Zmiana vs. stan obecny:** header każdej `wina/*.html` ma dziś dwa linki:
   > „Nasze odmiany" i „Sklep" (`../index.html#sklep`, ~w. 39–40). Link „Sklep" znika,
   > zostaje „Nasze odmiany".

3. Klika „Napisz do nas", trafia do formularza kontaktowego na stronie głównej i pisze
   zapytanie. Formularz nadal nic nie wysyła (`preventDefault` + `alert`), to znany stan
   demo (Gotchas / TODO). Poza zakresem tej zmiany.

| Element | Stan obecny | Po zmianie |
|---|---|---|
| Sekcja `#sklep` na stronie głównej | widoczna, filtry + siatka kart z `data/wina.json` | `hidden` — nie renderuje się, nie ma jej w widoku |
| Ikona koszyka w nagłówku | widoczna, otwiera panel koszyka | `hidden` |
| Panel koszyka (`#cart-overlay`, `#cart-panel`) | w DOM, otwierany przyciskiem | `hidden` |
| Menu główne | 6 pozycji (ze „Sklep", „Degustacje") | 4 pozycje (bez nich, z „Noclegi") |
| Stopka „Szybkie Linki" | O Nas · Nasze Wina · Sklep · Wydarzenia | O Nas · Nasze Wina · Wydarzenia · Noclegi |
| Podstrony odmian: link „w sklepie" / „Zobacz w sklepie" | → `#sklep` | → `#kontakt`, „Napisz do nas" |
| `data/wina.json`, panel cennika | źródło asortymentu i cen | **bez zmian** — nadal edytowalne, ceny widać na podstronach odmian |

### 3. Właściciel przegląda stronę po wdrożeniu i chce cofnąć ukrycie sklepu

**Persona:** Właściciel winnicy. Za kilka miesięcy ma pudełka i umowę z kurierem, chce
włączyć sprzedaż z powrotem. Nie chce, żeby ktoś odtwarzał sekcję sklepu od zera.

1. Otwiera `assets/js/main.js`, zmienia `const SKLEP_WLACZONY = false;` na `true`.
2. W `index.html` zdejmuje `hidden` z `<section id="sklep">`, `#cart-button`,
   `#cart-overlay`, `#cart-panel` i przywraca pozycje „Sklep" w menu (desktop, mobile,
   stopka) oraz przycisk hero.
3. W `wina/*.html` przywraca link „Sklep" i tekst „w naszym sklepie".

   **Za kulisami:** żaden kod logiki sklepu nie był ruszony, więc po zdjęciu `hidden`
   i włączeniu flagi `renderSklep()` / `initFilters()` / `initCart()` znów działają.
   `data/wina.json` przez cały czas był aktualny — Właściciel mógł dodawać wina panelem
   nawet przy ukrytym sklepie.

   > **Dlaczego flaga, a nie usunięcie kodu:** GUARDRAILS „Decision priorities" #3 stawia
   > czytelność diffu `index.html` wyżej niż elegancję. Usunięcie ~60 linii sekcji sklepu
   > + koszyk + gałęzie w `main.js`, a potem przywrócenie ich, to dwa duże, nieczytelne
   > diffy. `hidden` + flaga to zmiana punktowa, odwracalna jedną linią.

## Architecture

### Sklep: mechanizm ukrycia

Sklep wyłącza **jedna flaga w `main.js`** plus **atrybut `hidden`** na czterech elementach
`index.html`. Bez zmian w `wsgi.py`, `cennik.py`, `assets/js/produkty.js`, `data/wina.json`.

**`assets/js/main.js`:**

- Nowa stała u góry pliku, obok `themeStyles` / `stawkaVat`:
  ```js
  // Sprzedaż online wyłączona na start (SPEC-006). Sekcja #sklep i koszyk są `hidden`
  // w index.html; ta flaga wstrzymuje ich inicjalizację. Włączenie sprzedaży = `true`
  // + zdjęcie `hidden` z sekcji, koszyka i pozycji „Sklep" w nawigacji.
  const SKLEP_WLACZONY = false;
  ```
- W `DOMContentLoaded` (obecnie ~w. 918–933) blok sklepowy owinięty warunkiem:
  ```js
  if (SKLEP_WLACZONY) {
    cennik = await wczytajCennik();
    renderKategorie();
    if (renderSklep()) initFilters();
    initCart();
  }
  initWineOffer();
  ```
  **`initWineOffer()` zostaje poza warunkiem** — działa na podstronach `wina/*.html`
  (kontener `#oferta-odmiany`), które nie mają sekcji sklepu, a mają pokazywać ceny odmiany.
  `initWineOffer()` sam czyta globalne `cennik`, więc gdy sklep jest wyłączony, a jesteśmy
  na podstronie odmiany, `cennik` musi i tak zostać wczytany. Rozstrzygnięcie:
  `initWineOffer()` wczytuje cennik samodzielnie, jeśli nie zrobił tego blok sklepowy.
  ```js
  async function initWineOffer() {
    const wrap = qs("#oferta-odmiany");
    if (!wrap) return;
    if (!cennik) cennik = await wczytajCennik();   // podstrona odmiany bez bloku sklepowego
    ...
  }
  ```
  Wywołanie w `DOMContentLoaded` staje się `await initWineOffer();` (funkcja jest już
  `async`). **Sprawdzone w kodzie:** `wczytajCennik()` przy błędzie zwraca `null`
  (nie `{ wina: [] }`); istniejąca w `initWineOffer()` osłona `(cennik?.wina || [])`
  już to znosi — przy `null` zostaje tekst zastępczy z HTML-a. **Zmiana etykiety/linku:**
  „Zobacz w sklepie" → „Napisz do nas", `${KORZEN}index.html#sklep` →
  `${KORZEN}index.html#kontakt`.

**`index.html`:**

| Element | Kotwica | Zmiana |
|---|---|---|
| Sekcja sklepu | `<section id="sklep" class="py-20">` | dodać `hidden` |
| Przycisk koszyka | `<button id="cart-button" …>` | dodać `hidden` |
| Overlay koszyka | `<div id="cart-overlay" …>` | dodać `hidden` |
| Panel koszyka | `<aside id="cart-panel" …>` | dodać `hidden` |
| Menu desktop | `data-scroll="#sklep"` i `data-scroll="#degustacje"` | usunąć oba `<button>` |
| Menu mobile | jw. w `#mobile-menu` | usunąć oba `<button>` |
| Hero | dwa `<button class="btn-ghost">` | zastąpić jednym „Poznaj nasze wina" → `#nasze-wina` |
| Stopka „Szybkie Linki" | `<li>` z `data-scroll="#sklep"` | usunąć; dodać `<li>` „Noclegi" → `#noclegi` |

`openCart()` w `main.js` używa klasy `.open`, nie zdejmuje `hidden`. **Sprawdzone:**
wszystkie odwołania do `openCart()` i `#cart-button` (~w. 631, 637, 668) siedzą wewnątrz
`initCart()`, które przy `SKLEP_WLACZONY = false` w ogóle nie wystartuje. Nie ma zewnętrznego
wołacza — sama flaga wystarcza, `hidden` na `#cart-button` jest zabezpieczeniem wizualnym.

### Degustacje: usunięcie z treści

**`index.html`:**

- Nawigacja (desktop, mobile) — `data-scroll="#degustacje"` usunięte razem z pozycją „Sklep"
  (patrz tabela wyżej).
- Sekcja `#wydarzenia`:
  - `<h2>` „Wydarzenia i Degustacje" → „Wydarzenia".
  - `<p>` podtytuł „Degustacje i zwiedzanie winnicy organizujemy po wcześniejszym
    umówieniu…" → treść robocza: „Wyprzedaże, pikniki i spotkania sezonowe — ogłaszamy je
    z wyprzedzeniem na tej stronie." (**Właściciel dopisze wersję finalną.**)
  - Karta „Degustacje po umówieniu" — treść wymieniona (patrz „Karta typów wydarzeń").
    Atrybut `id="degustacje"` z `<h3>` **znika** (nie ma już do niego linku).
- Kontener `#lista-wydarzen` (`<div id="lista-wydarzen" … hidden>`) — **bez zmian**,
  `initWydarzenia()` nadal go wypełnia wpisami z panelu.

**`assets/js/main.js`:**

- Komentarze odwołujące się do „karty degustacji" (~w. 834, 875) — poprawić na
  „karta o wydarzeniach" / „statyczna karta w sekcji". Kod bez zmian.

**`wsgi.py`:**

- Komentarz w `zywe_wydarzenia()` (~w. 270): „…zostawi statyczna tresc o degustacjach"
  → „…zostawi statyczną treść sekcji wydarzeń". Kod bez zmian.

**`TODO.md`:**

- #13 „Wydarzenia i degustacje" i #15 (fragment o „wnętrzu do degustacji") — zamknąć jako
  nieaktualne po decyzji Właściciela (degustacji nie ma). #23 „Sklep obiecuje dostawę"
  — zamknąć (sekcja ukryta). #42 (jeśli wzmiankuje sklep) — dopisać notkę o ukryciu.
  **`TODO.md` jest dokumentem uzgadnianym z Właścicielem — zmiany wchodzą po jego akceptacji.**

### Karta typów wydarzeń

Zastępuje kartę „Degustacje po umówieniu" w sekcji `#wydarzenia`, w tym samym miejscu
(pod `#lista-wydarzen`) i w tym samym układzie dwukolumnowym
(`rounded-md border border-card-border overflow-hidden` + `grid md:grid-cols-2`).

Treść robocza (Właściciel poprawi):

- `<h3 class="font-serif text-2xl font-bold mb-5">` — „Co się u nas dzieje"
- `<p class="text-muted-foreground mb-8">` — „Nie prowadzimy stałego kalendarza. Kilka razy
  w roku organizujemy wyprzedaże roczników, pikniki na winnicy i spotkania przy zbiorach —
  terminy ogłaszamy tutaj i w mediach społecznościowych."
- `<ul class="space-y-2 mb-8">` (ten sam wzór punktów `w-1.5 h-1.5 rounded-full bg-primary`):
  - „Wyprzedaże i przedsprzedaże roczników"
  - „Pikniki i dni otwarte na winnicy"
  - „Spotkania przy zbiorach (winobranie)"
- `<button class="btn-primary" data-scroll="#kontakt">` — „Napisz do nas" (bez zmian)
- Kolumna zdjęcia: **zostaje** `attached_assets/generated_images/sala-degustacyjna-ai.jpg`
  z `alt="Wnętrze winiarni"`. Podmiana kadru na plenerowy jest opcjonalna i wykracza poza
  tę zmianę (nowy wpis w `TODO.md` zamiast starego #15).

Karta jest widoczna **zawsze**. Gdy panel ma aktywne wpisy, `initWydarzenia()` pokazuje je
w `#lista-wydarzen` **nad** kartą — tak jak dziś działa z kartą degustacji (SPEC-005,
User Story 2). Zachowanie „pusta lista → widać samą kartę" zostaje.

### Sekcja `#noclegi`

Nowy statyczny blok w `index.html`, **między** `</section>` sekcji `#wydarzenia`
a `<section id="kontakt">`.

Struktura (wzorowana na istniejących sekcjach — `max-w-7xl`, `py-20`, nagłówek wyśrodkowany
`data-reveal`, treść w `data-reveal`):

```html
<section id="noclegi" class="py-20 bg-secondary/20">
  <div class="max-w-7xl mx-auto px-5">
    <div class="text-center mb-12" data-reveal>
      <h2 class="font-serif text-3xl md:text-4xl font-bold mb-5">Nocleg w winnicy</h2>
      <p class="text-muted-foreground max-w-2xl mx-auto">Trzy pokoje w budynku winiarni,
        z widokiem na winorośl. Rezerwacja przez Booking.com.</p>
    </div>
    <!-- BEZ rzędu zdjęć na start — patrz „Zdjęcia" niżej. Realne 3 kadry pokoi
         doda Właściciel jako osobne zadanie. -->
    <div class="text-center" data-reveal>
      <a class="btn-primary is-disabled" aria-disabled="true" role="button" tabindex="-1"
         href="#noclegi">Zarezerwuj na Booking</a>
      <p class="text-sm text-muted-foreground mt-3">Rezerwacja wkrótce — link pojawi się niebawem.</p>
      <!-- TODO(SPEC-006 follow-up): podmienić href na URL oferty Booking od Właściciela,
           usunąć aria-disabled / is-disabled i podpis „Rezerwacja wkrótce". -->
    </div>
  </div>
</section>
```

Decyzje:

- **`bg-secondary/20`** — naprzemienne tło jak `#o-nas` i `#nasze-wina`. **Rozstrzygnięte
  w przeglądzie:** zostaje `bg-secondary/20`. Sąsiednie `#wydarzenia` i `#kontakt` są bez
  tła, więc lekki tint wyraźnie oddziela sekcję noclegów — wygląda dobrze we wszystkich
  czterech motywach.
- **Przycisk nieaktywny:** `<a>` bez roboczego `href` do Bookinga. Wariant przyjęty:
  `href="#noclegi"` (kotwica do samej siebie — bezpieczna, nie przewija), `aria-disabled`,
  `tabindex="-1"`, klasa `is-disabled`. **Nie wpisywać zmyślonego URL-a Booking**
  (GUARDRAILS / Gotchas: „NEVER invent URLs"). Alternatywa: zwykły `<span>` ostylowany
  jak przycisk. Wybór przy implementacji — obie są OK, `<a>` upraszcza późniejszą podmianę.
- **Klasa `is-disabled`** — **sprawdzone:** nie ma jej w bundlu
  (`grep -c 'is-disabled' assets/css/style.css` → 0). Dopisać do `assets/css/custom.css`:
  `opacity` + `pointer-events: none` + `cursor: default`. Nowa klasa CSS **nie jest
  zmienną motywu**, więc BLOCK #1 z GUARDRAILS nie dotyczy — ale i tak przejrzeć
  w czterech motywach (kontrast wyszarzonego przycisku).
- **Zdjęcia — na start sekcja jest BEZ zdjęć.** **Sprawdzone:** ani
  `attached_assets/generated_images/` (tylko `sala-degustacyjna-ai.jpg` i
  `Green_wine_grapes_closeup_*.jpg`), ani `attached_assets/photos/` nie zawierają kadru
  pokoju czy wnętrza sypialnego — same winnice, kiście, butelki, zbiory. Wstawianie tu
  panoramy winnicy jako „pokoju" wprowadzałoby w błąd. Sekcja startuje jako
  nagłówek + zajawka + przycisk. Realne 3 kadry pokoi Właściciel prześle — wtedy osobne,
  małe zadanie: wgranie do `attached_assets/photos/`, rząd `grid md:grid-cols-3`, `alt`-y,
  `width`/`height`, `loading="lazy"`.
- **Nawigacja:** „Noclegi" → `data-scroll="#noclegi"` w menu desktop i mobile
  (po „Wydarzenia", przed „Kontakt"), oraz `<li>` w stopce „Szybkie Linki".
- **`sitemap.xml`** — zawiera tylko adresy stron (`/`, `/wina/*`), nie kotwice sekcji.
  Sprawdzić i potwierdzić, że nie wymaga wpisu.

### Teksty do poprawy przez Właściciela (workstream F)

Poza zakresem kodu tej zmiany, ale spec je odnotowuje, żeby nie zginęły:

- Hero: „Tradycyjne wina z **bieszczadzkich** stoków" — winnica jest w Kielnarowej pod
  Rzeszowem. Właściciel poda nową wersję.
- „tradycyjne" → „kraftowe" / „rzemieślnicze" — decyzję ułatwia przełącznik `?slowo=`
  (quick-spec 004). Domyślna treść w `index.html` zmieni się dopiero, gdy Właściciel
  wskaże słowo.
- Podtytuł sekcji „Wydarzenia" i treść karty typów wydarzeń — wersje robocze w tej specie.

## Data Models

Brak zmian. `data/wina.json` i `data/wydarzenia.json` — struktura i moduły (`cennik.py`,
`wydarzenia.py`) nietknięte. Sekcja `#noclegi` nie ma danych — jest w całości w `index.html`.

## API Contracts

Brak zmian. Żadna trasa `wsgi.py` nie jest dodawana ani modyfikowana (poza jednym
komentarzem). `/data/wina.json`, `/data/wydarzenia.json`, panel — bez zmian.

## UI/UX

- **Nawigacja** — cztery pozycje: `O Nas · Nasze Wina · Wydarzenia · Noclegi · Kontakt`
  (pięć etykiet; „Nasze Wina" i „Wydarzenia" zostają). Desktop `flex`, mobile menu
  rozwijane — obie listy w `index.html` trzymać w parytecie.
- **Hero** — jeden przycisk `btn-ghost` „Poznaj nasze wina". `initNavigation()` bez zmian.
- **Sekcja `#sklep`** — `hidden`, całkowicie poza widokiem i poza kolejnością tabulacji.
- **Koszyk** — `#cart-button`, `#cart-overlay`, `#cart-panel` `hidden`.
- **Sekcja `#wydarzenia`** — nagłówek „Wydarzenia", pod listą wpisów karta „Co się u nas
  dzieje" (dwie kolumny, zdjęcie + tekst + `btn-primary` do `#kontakt`).
- **Sekcja `#noclegi`** — nagłówek wyśrodkowany, zajawka, przycisk wyśrodkowany + podpis
  „Rezerwacja wkrótce". Przycisk wyszarzony, nieklikalny. Bez zdjęć na start; gdy dojdą
  kadry pokoi — rząd `grid md:grid-cols-3` (na telefonie jedna kolumna) nad przyciskiem.
- **Podstrony `wina/*.html`** — header bez „Sklep"; blok `#oferta-odmiany` kieruje do
  `#kontakt`. `soki.html`: `<h2>` „Soki w naszym sklepie" → „Soki z naszej winnicy".
- **Motywy** — nowa sekcja `#noclegi`, karta typów wydarzeń i ewentualna klasa
  `.is-disabled` sprawdzone w `classic`, `modern`, `rustic`, `dark`. Kolory tylko przez
  `hsl(var(--…))` (GUARDRAILS BLOCK #2).
- **Diff `index.html`** — zmiany punktowe, bez przeformatowania (GUARDRAILS BLOCK #5).
  Nowa sekcja `#noclegi` to jeden spójny blok wstawiony w jednym miejscu.

## Configuration

Brak nowych zmiennych środowiskowych ani flag konfiguracyjnych po stronie serwera.
Jedyna „flaga" to `const SKLEP_WLACZONY` w `assets/js/main.js` — stała w kodzie, nie
konfiguracja runtime. Świadomie: sprzedaż online wraca przez zmianę kodu i przegląd,
nie przez przełącznik dla użytkownika.

## Kryteria akceptacji

**Sklep i koszyk**

- Sekcja `#sklep` nie jest widoczna ani osiągalna tabulacją na stronie głównej.
- Ikona koszyka i panel koszyka nie są widoczne.
- W konsoli przeglądarki brak błędów przy `SKLEP_WLACZONY = false` (żaden `initX` sklepowy
  nie odwołuje się do nieistniejącego węzła).
- `data/wina.json` bez zmian; panel cennika działa jak przed zmianą (jeśli włączony).
- Zmiana `SKLEP_WLACZONY = true` + zdjęcie `hidden` z czterech elementów przywraca w pełni
  działający sklep i koszyk (weryfikacja: diff zachowania względem `master`).

**Nawigacja**

- Menu desktop i mobile: `O Nas · Nasze Wina · Wydarzenia · Noclegi · Kontakt`. Brak
  „Sklep" i „Degustacje".
- Stopka „Szybkie Linki": `O Nas · Nasze Wina · Wydarzenia · Noclegi`.
- `grep -n '#degustacje' index.html` → 0 trafień. `grep -n '#sklep' index.html` → 0
  (poza ewentualnym zakomentowanym kodem, którego tu nie ma — sekcja jest `hidden`, nie
  usunięta, ale `data-scroll="#sklep"` znika).
- Hero: jeden przycisk „Poznaj nasze wina" → przewija do `#nasze-wina`.

**Degustacje**

- Żadna widoczna treść strony głównej nie zawiera słowa „degustacj-" poza ewentualnym
  neutralnym użyciem w treści karty typów wydarzeń, jeśli Właściciel je zostawi.
- Nagłówek sekcji to „Wydarzenia".
- `initWydarzenia()` nadal wstawia wpisy z panelu nad kartę „Co się u nas dzieje".
- Pusta lista wydarzeń → widać samą kartę typów wydarzeń, bez błędu.

**Noclegi**

- Sekcja `#noclegi` jest między `#wydarzenia` a `#kontakt`, widoczna, z nagłówkiem,
  zajawką i przyciskiem. **Bez rzędu zdjęć** (brak kadrów pokoi w zasobach — dojdą osobno).
- Przycisk „Zarezerwuj na Booking" jest wyszarzony, `aria-disabled="true"`, nie przewija
  strony ani nigdzie nie prowadzi. Pod nim podpis „Rezerwacja wkrótce".
- **W repozytorium nie ma zmyślonego adresu Booking** — `href` wskazuje `#noclegi`
  albo element to `<span>`.
- Sekcja czytelna w czterech motywach i na szerokości telefonu.

**Podstrony odmian**

- `wina/*.html` (8 plików): header bez linku „Sklep".
- Blok `#oferta-odmiany`: tekst zastępczy i przycisk `initWineOffer()` kierują do
  `#kontakt`, nie `#sklep`.
- Gdy `data/wina.json` ma pozycje z danej odmiany — nazwy i ceny nadal się renderują.
- `soki.html`: nagłówek „Soki z naszej winnicy".

**Ogólne**

- Diff `index.html` jest punktowy, bez przeformatowania niezwiązanych fragmentów.
- Wszystkie zestawy testów przechodzą: `test-routing`, `test-wydarzenia`,
  `test-cennik-sciezka`, `test-panel-auth`, `test-serwowanie`. Żaden nie zależał od
  widoczności sklepu; potwierdzić `grep -rn 'sklep\|cart\|degustacj' tools/test-*.py`.
- `?hero=` nadal działa (pasek wyboru kadru hero).

## Implementation Checklist

- [x] Wstrzyknąć standardy: `content/html-editing`, `content/wina-json`,
  `frontend/js-conventions`, `frontend/styling`, `frontend/theming` (wczytane przez Read —
  `/inject-standards` niedostępny w tym klonie, `.claude/` w `.gitignore`).
- [x] `assets/js/main.js` — stała `SKLEP_WLACZONY = false`, warunek wokół bloku sklepowego
  w `DOMContentLoaded`, `initWineOffer()` jest `async` i sam dociąga `cennik` (`wczytajCennik()`
  zwraca `null` przy błędzie — osłona `(cennik?.wina || [])` już to znosi), etykieta/link
  „Napisz do nas" → `#kontakt`, poprawione komentarze o „karcie degustacji".
- [x] `index.html` — `hidden` na `#sklep`, `#cart-button`, `#cart-overlay`, `#cart-panel`;
  menu (desktop + mobile) bez „Sklep" i „Degustacje", z „Noclegi"; hero jeden przycisk
  „Poznaj nasze wina" → `#nasze-wina`; nagłówek sekcji „Wydarzenia" + nowy podtytuł;
  karta „Co się u nas dzieje" (bez `id="degustacje"`); nowa sekcja `#noclegi`; stopka
  „Szybkie Linki".
- [x] `assets/css/custom.css` — `[hidden]{display:none!important}` (atrybut `hidden` musi
  wygrywać z utility Tailwinda ustawiającymi `display` — bez tego `#cart-button`/`#cart-panel`
  zostawały widoczne); klasa `.is-disabled` dla przycisku noclegów — nadpisuje tło/kolor
  `.btn-primary` tokenami `--muted` / `--muted-foreground` / `--border` (samo `opacity`
  gubiło kontrast na `dark`).
- [x] `wina/*.html` (8) — header bez „Sklep"; `#oferta-odmiany` tekst zastępczy →
  „Napisz do nas po aktualną dostępność — formularz kontaktowy" → `#kontakt`;
  `soki.html` nagłówek „Soki z naszej winnicy".
- [x] `wsgi.py` — jeden komentarz w `zywe_wydarzenia()`.
- [x] `TODO.md` — zamknięte #13, #23; #15 zaktualizowane (pokoje zamiast wnętrza degustacji);
  nowe #37 „Noclegi: link Booking + zdjęcia" i #38 „Sklep ukryty flagą — jak przywrócić";
  data aktualizacji → 2026-09-06.
- [x] `.ai/GUARDRAILS.md` — nowy punkt #6 w „Architectural boundaries": sklep wyłączony
  flagą `SKLEP_WLACZONY`, nie usuwać kodu koszyka bez decyzji Właściciela.
- [x] Przegląd w przeglądarce (dev-server, port 5052) — cztery motywy, wina/dornfelder.html,
  konsola bez błędów. Szczegóły w „Implementation Review".
- [x] Testy `tools/test-*.py` — `test-routing`, `test-wydarzenia`, `test-cennik-sciezka`,
  `test-panel-auth` przechodzą; `test-serwowanie` pominięty (brak Flaska lokalnie).
  `/verify-standards` niedostępny (`.claude/` w `.gitignore`).
- [ ] `/sync-standards` — niedostępny w tym klonie; zmiany do standardów dopisać ręcznie,
  jeśli utrwalone (żadna nowa reguła kodu nie wynikła — `[hidden]` reset i `.is-disabled`
  są opisane w kodzie i w tej specyfikacji).

## Implementation Review

Przegląd na `python3 tools/dev-server.py` (statyczny `http.server`, bez serwerowej podmiany
hero i bez `no-cache` na CSS — **wnioski o cache niżej**).

**Strona główna**

- Nawigacja desktop i mobile: `O Nas · Nasze Wina · Wydarzenia · Noclegi · Kontakt`.
  Brak „Sklep" i „Degustacje", brak ikony koszyka. Stopka „Szybkie Linki": bez „Sklep",
  z „Noclegi".
- `#sklep`, `#cart-button`, `#cart-overlay`, `#cart-panel` → `display: none` (po dodaniu
  `[hidden]{display:none!important}` — patrz niżej). `grep '#sklep' / '#degustacje'`
  w `index.html` → 0 `data-scroll`.
- Hero: jeden przycisk „Poznaj nasze wina", przewija do `#nasze-wina`.
- Sekcja „Wydarzenia": nagłówek „Wydarzenia", karta „Co się u nas dzieje" (wyprzedaże /
  pikniki / spotkania przy zbiorach, CTA „Napisz do nas" → `#kontakt`).
- Sekcja `#noclegi` między `#wydarzenia` a `#kontakt`: nagłówek, zajawka, przycisk
  „Zarezerwuj na Booking" wyszarzony (`aria-disabled`, `pointer-events: none`,
  `href="#noclegi"` — nie przewija), podpis „Rezerwacja wkrótce". Bez zdjęć.
- Cztery motywy — przycisk `.is-disabled` idzie za tokenami:
  classic `#ebe7e0`/`#595959`, modern `#f0f0f0`/`#666`, rustic `#e7e1da`/`#756357`,
  dark `#20232?`/`#a4acb7`. Tło sekcji `bg-secondary/20` odróżnia ją od białego `#kontakt` —
  zostaje.
- Konsola bez błędów; kliknięcia nawigacji bez wyjątków.

**Podstrony odmian** (`wina/dornfelder.html`)

- Header: tylko „Nasze odmiany", bez „Sklep". Brak `#sklep` w całym dokumencie.
- `#oferta-odmiany`: `initWineOffer()` dociągnął cennik mimo `SKLEP_WLACZONY = false`,
  wyrenderował „Dornfelder - 2022 — 157.00 zł", CTA „Napisz do nas" →
  `…/index.html#kontakt`. Konsola czysta.

**Znalezione i naprawione w trakcie przeglądu**

- **`hidden` nie chował `#cart-button` ani `#cart-panel`** — mają utility/klasy ustawiające
  `display` (`inline-flex`, `.cart-panel{display:flex}`), które biją regułę UA `[hidden]`.
  Dodane `[hidden]{display:none!important}` w `custom.css` (dotyczy atrybutu, nie klasy
  `.hidden`). Sekcja `#sklep` i `#cart-overlay` chowały się już wcześniej.
- **`.is-disabled` na samym `opacity: 0.55`** — na motywie `dark` przycisk (`.btn-primary`
  = ciemny grafit) na ciemnym tle znikał. Zmienione na nadpisanie tła/koloru/ramki
  tokenami `--muted` / `--muted-foreground` / `--border`; kontrast poprawny we wszystkich
  czterech motywach.

**Uwaga narzędziowa (nie dotyczy produkcji)** — `tools/dev-server.py` serwuje CSS bez
`no-cache`, więc przeglądarka trzymała starą wersję `custom.css` między edycjami; przy
podglądzie zmian CSS trzeba wymuszać przeładowanie (`?v=` albo świeży port). Na produkcji
`wsgi.py` daje CSS `no-cache` + ETag, więc problem tam nie istnieje (TODO #35).

## Changelog

### 2026-09-06

- Pierwsza wersja specyfikacji: pivot oferty na start — sprzedaż online ukryta (flaga
  `SKLEP_WLACZONY` + `hidden`, bez usuwania kodu), degustacje zdjęte z treści, karta
  „Degustacje po umówieniu" zastąpiona kartą typów wydarzeń, nowa sekcja `#noclegi`
  z nieaktywnym przyciskiem Booking (bez zmyślonego URL-a).
- Odnotowane zależności: SPEC-005 (wydarzenia w panelu) nietknięte; teksty Właściciela
  (hero „bieszczadzkich", słowo „tradycyjne") poza zakresem kodu; przełącznik `?slowo=`
  wydzielony do `.ai/specs/quick/004-przelacznik-slowa-tradycyjne.md`.
- Ripple na `wina/*.html` (8 plików) rozpisany: link „Sklep" w headerze i odwołania
  „w sklepie" w `#oferta-odmiany` przekierowane do `#kontakt`.
- Wdrożone i sprawdzone w przeglądarce (cztery motywy, podstrona odmiany, konsola czysta).
  Dwie poprawki w trakcie: `[hidden]{display:none!important}` w `custom.css` (atrybut `hidden`
  przegrywał z utility Tailwinda na `#cart-button` / `#cart-panel`); `.is-disabled` przeszło
  z samego `opacity` na nadpisanie tła/koloru tokenami `muted`, bo na `dark` przycisk znikał.
  `TODO.md`: #13 i #23 zamknięte, #15 zaktualizowane, nowe #37 (link + zdjęcia Booking)
  i #38 (jak przywrócić sklep). `GUARDRAILS.md`: nowy punkt #6 w „Architectural boundaries".
