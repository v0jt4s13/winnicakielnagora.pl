# SPEC-001 — Sklep z pliku JSON i strony odmian pod SEO

**Status**: propozycja do akceptacji
**Rozmiar**: L
**Data**: 2026-09-02

## Overview

Witryna `winnicakielnagora.pl` jest dziś w całości demonstracyjna: produkty, wydarzenia, dane
kontaktowe i wszystkie zdjęcia są zmyślone albo wygenerowane przez AI. Właściciel dostarczył
prawdziwe materiały (`docs/materialy-do-wykorzystania/`, poza repozytorium) i podjął dwie
decyzje kierunkowe:

1. **Lista win i cennik pochodzą z zewnętrznego pliku danych** (`data/wina.json`), edytowalnego
   bez dotykania HTML-a i JS-a.
2. **Strona musi być widoczna dla wyszukiwarek.** Sklep może się budować przez `fetch` + JS, ale
   każda odmiana wina dostaje **rozbudowaną statyczną stronę (landing page)** z linkiem do sklepu.

Ta specyfikacja opisuje jedno i drugie oraz podmianę pozostałych atrap na dane, które już znamy.

### Zakres

- `data/wina.json` — jedyne źródło asortymentu i cen.
- Przepisanie sekcji `#sklep` z markupu zaszytego w `index.html` na render z JSON-a.
- Siedem statycznych stron odmian w `wina/` (SEO: pełna treść w HTML).
- Podmiana zdjęć AI na prawdziwe w sekcjach `#o-nas`, `#nasze-wina`, hero i stopce.
- Poprawienie faktów o winnicy w `#o-nas` i stopce.
- `sitemap.xml`, `robots.txt`, znaczniki meta, Open Graph i JSON-LD.

### Poza zakresem

- Prawdziwa sprzedaż (płatności, trwały koszyk) — koszyk zostaje zaślepką demo, patrz `TODO.md` #7.
- Wysyłka formularza kontaktowego — bez backendu, patrz `TODO.md` #7.
- Sekcje `#kontakt` i `#wydarzenia` — czekają na dane od Właściciela (`TODO.md` #9 i #13).
  Ta specyfikacja ich **nie rusza**, żeby nie utrwalać atrap.
- Filmy z `docs/` — decyzja odłożona (`TODO.md` #16).

## Blokady — przeczytaj przed rozpoczęciem

Implementacja **nie może ruszyć w całości**, dopóki nie zostaną zdjęte trzy blokady. Każda
z nich należy do Właściciela; sesja implementująca nie ma prawa ich rozstrzygnąć sama.

| # | Blokada | Co blokuje | Gdzie |
|---|---|---|---|
| B1 | Brak asortymentu i cennika | **treść** `data/wina.json` (nie strukturę) | `TODO.md` #10 |
| ~~B2~~ | ~~Brak zgody na zmianę `.ai/GUARDRAILS.md`~~ | **ZDJĘTA 2026-09-02** | `.ai/GUARDRAILS.md` |
| ~~B3~~ | ~~Status odmiany Swenson Red~~ | **ZDJĘTA 2026-09-02** — Właściciel potwierdził, że wino Swenson Red jest produkowane | — |

Wszystkie blokady zdjęte. Zostaje jedynie B1, i tylko w części dotyczącej treści pliku.

**B1 nie blokuje tyle, ile się wydaje.** Plik `data/wina.json` powstaje od razu, z pustą tablicą
`wina` i wypełnionymi `waluta`, `stawka_vat`, `kategorie`. Cały mechanizm sklepu da się na nim
zbudować i przetestować, a asortyment wprowadzi Właściciel **panelem redakcyjnym**
(`.ai/specs/SPEC-002-*`) — to właśnie narzędzie, którym B1 się zamyka. Pusta lista musi dawać
sensowny komunikat („Oferta w przygotowaniu"), a nie pustą sekcję.

**Co da się zrobić mimo blokad** (i co należy zrobić najpierw): cały mechanizm sklepu na pustym
`data/wina.json`, strony odmian dla sześciu potwierdzonych odmian, podmiana zdjęć AI na
prawdziwe, poprawki faktów w `#o-nas`, stopce i `<title>`, `sitemap.xml`, `robots.txt`,
znaczniki meta.

### Zasada dotycząca treści, których nie znamy

Priorytet #1 z `.ai/GUARDRAILS.md` brzmi „Poprawność treści publicznej". W praktyce:

- **Fakty o odmianie** (charakter, aromaty, odporność, typowe zastosowanie) wolno napisać
  na podstawie źródeł publicznych wskazanych przez Właściciela — lista niżej.
- **Fakty o tej konkretnej winnicy** (kiedy zasadzono daną odmianę, ile jest krzewów, kiedy
  zbiór, jakie wino z niej powstaje) wolno napisać **wyłącznie** na podstawie sekcji
  „Materiały źródłowe" poniżej. Czego tam nie ma — tego się nie pisze.
- Jeśli w szablonie strony zostaje miejsce bez treści, wstaw komentarz HTML
  `<!-- TODO: potwierdzić z Właścicielem -->` i dopisz pozycję do `TODO.md`.
  **Nie wymyślaj faktów o winnicy, nawet prawdopodobnych.**

## Materiały źródłowe

Katalog `docs/` jest w `.gitignore` (580 MB), więc świeża sesja go nie zobaczy. Wszystko, co
z niego potrzebne, jest przepisane tutaj.

### Opis winnicy — jedyne potwierdzone fakty

> Winnica Kielna Góra
> Położona na stoku o południowym nachyleniu w Kielnarowej, 10 km od centrum Rzeszowa,
> założona w 2024 roku, pierwsze nasadzenia w 2020 roku.
> Niewielka, jednohektarowa.
> Uprawiamy winogrona na wina białe: Souvignier Gris, St Pepin, Vidal Blanc, Seyval Blanc,
> a także na wina czerwone i różowe odmian Monarch i Dornfelder.
> Wytwarzamy również soki z białych winogron, 100% naturalne, bez żadnych dodatków.

(cytat z `docs/materialy-do-wykorzystania/zbiory_i_winnica/Winnica Kielna Góra.txt`)

Uwaga: **ten opis nie wymienia Swenson Red** — stąd blokada B3.

### Źródła opisów odmian (wskazane przez Właściciela)

| Odmiana | Źródło |
|---|---|
| Dornfelder | `https://pl.wikipedia.org/wiki/Dornfelder` |
| Seyval Blanc | `https://pl.wikipedia.org/wiki/Seyval_blanc` |
| Souvignier Gris | `https://en.wikipedia.org/wiki/Souvignier_gris` |
| St. Pepin | `https://en.wikipedia.org/wiki/St._Pepin_(grape)` |
| Vidal Blanc | `https://en.wikipedia.org/wiki/Vidal_blanc` |
| Swenson Red | `https://en.wikipedia.org/wiki/Swenson_Red` |
| Monarch | `https://www.rebschule-sester.de/en/variety-description/fungus-resistant-red-varieties/monarch/` |

Adresy pochodzą z plików `.txt` dołączonych przez Właściciela do każdego folderu z materiałami —
nie zostały wymyślone. Przed użyciem jako źródła treści **zweryfikuj każdy przez WebFetch**;
jeśli któryś nie odpowiada, zapytaj Właściciela zamiast szukać zamiennika.

### Domena produkcyjna

`https://winnicakielnagora.pl` — potwierdzona przez Właściciela jako docelowa. **Projekt nie
jest jeszcze dostępny online**; pod tym adresem stoi dziś placeholder. Domena występuje
w `<link rel="canonical">`, Open Graph i `sitemap.xml`; przy zmianie trzeba ją podmienić
w tych trzech miejscach oraz w `robots.txt`.

## Stan obecny (co trzeba znać przed zmianą)

- `index.html` (~790 linii) to jedyna strona. Sekcje: `#o-nas`, `#nasze-wina`, `#sklep`,
  `#wydarzenia`, `#kontakt`. Ikony jako `<symbol>` w ukrytym `<svg>` na początku `<body>`.
- Produkty to sześć elementów `<article class="product-card">` z atrybutami `data-id`,
  `data-name`, `data-category`, `data-price`, `data-promo`, `data-image` (czytanymi przez JS)
  oraz `data-price-net` i `data-discount` (martwymi). Ceny są przepisane ręcznie w sześciu
  miejscach każdej karty.
- `assets/js/main.js` (463 linie): `themeStyles` (3 motywy × 29 zmiennych CSS), `setTheme`,
  `initStyleSwitcher`, `initNavigation`, `initFilters`, `renderCart`, `initCart`,
  `initContactForm`, spięte w `DOMContentLoaded`.
- `assets/css/style.css` to zbudowany bundle Tailwinda **bez źródeł** — nowej klasy utility nie
  da się dobudować. Style własne idą do `assets/css/custom.css`.
- `wsgi.py` serwuje katalog repo i **na każdą nieznaną ścieżkę oddaje `index.html` ze statusem
  200** (nigdy 404).
- Zoptymalizowane zdjęcia leżą już w `attached_assets/photos/` — 41 zdjęć w dwóch wariantach:
  `<slug>.jpg` (dłuższy bok 1600 px) i `<slug>-sm.jpg` (600 px). Generuje je
  `tools/optimize-photos.py` z `docs/` (katalog jest w `.gitignore`).

## User Stories

### Story 1 — Marek szuka wina w Google (SEO, happy path)

**Persona**: Marek, 41 lat, mieszka w Rzeszowie, szuka lokalnego wina na prezent. Wpisuje
w wyszukiwarkę „souvignier gris podkarpacie". Nie zna marki winnicy — trafia z wyników, nie ze
strony głównej.

**Krok 1.** Google pokazuje wynik z tytułem i opisem strony odmiany.

```
┌──────────────────────────────────────────────────────────┐
│ Souvignier Gris — biała odmiana z Winnicy Kielna Góra     │
│ winnicakielnagora.pl › wina › souvignier-gris            │
│ Odporna odmiana o aromatach brzoskwini i cytrusów.       │
│ Uprawiana na południowym stoku w Kielnarowej pod Rzeszowem│
└──────────────────────────────────────────────────────────┘
```

> **Za kulisami**: plik `wina/souvignier-gris.html` istnieje fizycznie na dysku i zawiera całą
> treść w HTML — bez JavaScriptu. Robot pobiera go jednym żądaniem. `<title>`,
> `<meta name="description">`, `<link rel="canonical">`, Open Graph i JSON-LD są w `<head>`.

**Krok 2.** Marek wchodzi na stronę odmiany.

```
┌────────────────────────────────────────────────────────────┐
│ ← Winnica Kielna Góra              [Nasze wina] [Sklep]    │
├────────────────────────────────────────────────────────────┤
│  ███████████████  zdjęcie kiści (souvignier-gris-kiscie-02)│
│                                                            │
│  Souvignier Gris                                           │
│  Biała odmiana · uprawiana od 2020 · zbiór wrzesień        │
│                                                            │
│  Odporna odmiana o aromatach brzoskwini i cytrusów…        │
│  [2-3 akapity treści + charakterystyka + jak ją uprawiamy] │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Wina z tej odmiany                                   │  │
│  │ Souvignier Gris 2024 · wytrawne · 12% · 750 ml       │  │
│  │ 65,00 zł         [ Zobacz w sklepie → ]              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

> **Za kulisami**: treść odmiany jest statyczna. Blok „Wina z tej odmiany" wypełnia
> `initWineOffer()` z `data/wina.json` — filtruje pozycje po `odmiana_slug === "souvignier-gris"`.
> Zanim JSON się wczyta (albo gdy `fetch` padnie), w bloku stoi statyczny tekst zastępczy
> „Sprawdź dostępność w sklepie" z linkiem — strona **nigdy** nie pokazuje pustego miejsca.

**Zmiana vs. stan obecny**: dziś takie strony nie istnieją. Wpisanie „souvignier gris" prowadzi
w najlepszym razie na stronę główną, gdzie odmiana jest jednym z siedmiu kafelków bez własnego
adresu. Po zmianie każda odmiana ma własny adres, tytuł i opis w wynikach wyszukiwania.

**Krok 3.** Marek klika „Zobacz w sklepie" i trafia na `/index.html#sklep` z ustawionym filtrem
kategorii (parametr `?kategoria=biale`), więc widzi od razu białe wina.

### Story 2 — Anna przegląda sklep (ścieżka wewnątrz strony)

**Persona**: Anna, 33 lata, weszła na stronę główną z Facebooka. Chce zobaczyć, co jest
w ofercie i w jakiej cenie. Przegląda na telefonie.

**Krok 1.** Anna przewija do sekcji „Sklep".

```
┌──────────────────────────────────┐
│  Filtry            [Wyczyść]     │
│  Typ:  ( Wszystkie )( Białe ) …  │
│  Cena: 25 ————•———— 89 zł        │
│  ☐ Tylko promocje                │
├──────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  │
│  │  [zdjęcie] │  │  [zdjęcie] │  │
│  │ Souvignier │  │ Monarch    │  │
│  │ Gris 2024  │  │ 2023  -10% │  │
│  │ 65,00 zł   │  │ 58,50 zł   │  │
│  │ netto 52,85│  │ 65,00 zł ̶  │  │
│  │ [ Dodaj ]  │  │ [ Dodaj ]  │  │
│  └────────────┘  └────────────┘  │
└──────────────────────────────────┘
```

> **Za kulisami**: `initShop()` pobiera `data/wina.json`, renderuje karty do
> `#lista-produktow`, a dopiero potem uruchamia `initFilters()` i podpina przyciski koszyka.
> Suwak ceny dostaje `min`/`max` policzone z danych, nie zaszyte na 0–100.

**Zmiana vs. stan obecny**: dziś karty są zaszyte w `index.html`, a suwak ma na sztywno zakres
0–100 zł — wino droższe niż 100 zł znikałoby z listy bez komunikatu. Cena netto i przekreślona
cena sprzed rabatu są dziś przepisywane ręcznie i już raz się rozjechały (`TODO.md` #1).
Po zmianie obie są **wyliczane**: `netto = brutto / 1.23`, `cena sprzed rabatu = brutto / (1 − rabat/100)`.

**Krok 2.** Anna klika nazwę wina na karcie → trafia na stronę odmiany (Story 1, krok 2).
Karta produktu linkuje do `wina/<odmiana_slug>.html`.

### Story 3 — Właściciel podnosi cenę (edge case, utrzymanie)

**Persona**: Właściciel winnicy. Nie programuje. Chce zmienić cenę jednego wina i oznaczyć dwa
inne jako niedostępne — bez wołania kogokolwiek.

**Krok 1.** Otwiera `data/wina.json` w dowolnym edytorze tekstu i zmienia dwie liczby oraz
jedno `true` na `false`. Zapisuje, wgrywa plik na serwer.

> **Za kulisami**: nie ma builda ani bazy. Plik jest serwowany statycznie, przeglądarka pobiera
> go przy każdym wejściu. Zmiana jest widoczna po odświeżeniu strony.

**Krok 2.** Wino oznaczone `"dostepne": false` znika ze sklepu, ale **strona odmiany zostaje** —
z informacją „chwilowo niedostępne" zamiast ceny. Adres, który zdążył zaindeksować Google, nie
przestaje działać.

> **Za kulisami**: `initShop()` pomija pozycje z `dostepne: false`. `initWineOffer()` na stronie
> odmiany pokazuje je z etykietą zamiast przycisku.

**Zmiana vs. stan obecny**: dziś zmiana ceny to edycja sześciu miejsc w markupie jednej karty
(`data-price`, `data-price-net`, widoczna cena, tekst „netto", przekreślona cena, badge `-N%`)
i nic tego nie waliduje. Po zmianie to jedna liczba w jednym pliku.

### Porównanie: dziś vs. po zmianie

| | Dziś | Po zmianie |
|---|---|---|
| Źródło asortymentu | markup w `index.html` | `data/wina.json` |
| Zmiana ceny | 6 miejsc w karcie, ręcznie | 1 pole w JSON |
| Cena netto, rabat | przepisane ręcznie | wyliczane w JS |
| Zakres filtra cen | zaszyty 0–100 zł | liczony z danych |
| Adres odmiany | brak | `/wina/<slug>.html` |
| Treść dla robotów | wszystko w `index.html` | + 7 stron z unikalną treścią |
| Zdjęcia | 9 grafik AI | prawdziwe zdjęcia z winnicy |

## Architektura

```
index.html                    # strona główna; #sklep renderowany z JSON
wina/
  souvignier-gris.html        # 7 statycznych stron odmian, pelna tresc w HTML
  st-pepin.html
  vidal-blanc.html
  seyval-blanc.html
  monarch.html
  dornfelder.html
  swenson-red.html
data/
  wina.json                   # JEDYNE zrodlo asortymentu i cen
assets/js/produkty.js         # renderProductCard() + wyliczenia cen - wspoldzielone z panelem
assets/js/main.js             # + initShop(), initWineOffer(); laduje sie PO produkty.js
attached_assets/photos/       # zoptymalizowane zdjecia (juz sa)
sitemap.xml, robots.txt       # nowe, w katalogu glownym
tools/optimize-photos.py      # generator zdjec (juz jest)
```

**Przepływ danych**

```
data/wina.json ──fetch──> initShop()        ──> karty w #lista-produktow ──> initFilters(), koszyk
               └─fetch──> initWineOffer()   ──> blok "Wina z tej odmiany" na stronie odmiany
```

### Kontrakt `assets/js/produkty.js`

Renderowanie karty produktu i wyliczenia cen mieszkają w **osobnym pliku**, a nie w `main.js`.
Powód: panel redakcyjny (SPEC-002) pokazuje podgląd karty i musi używać dokładnie tego samego
kodu, co sklep — inaczej podgląd zacznie kłamać. `main.js` nie da się w tym celu wczytać
w panelu, bo jego `DOMContentLoaded` odpala całą inicjalizację strony (nawigację, motywy,
koszyk), której w panelu nie ma i nie powinno być.

`produkty.js` to zwykły skrypt bez `import`/`export` (zgodnie z `.ai/GUARDRAILS.md` → „Front-end
bez frameworka i bez modułów"), definiujący jeden globalny obiekt. **Nie ma w nim żadnego
`addEventListener` ani odwołania do DOM strony głównej** — wczytanie go niczego nie uruchamia.

```js
// assets/js/produkty.js
const Produkty = {
  // { netto, brutto, przedRabatem|null, promocja }  — wszystkie liczby, nie napisy
  policzCeny(wino, stawkaVat),

  // zwraca STRING z HTML-em jednej karty (nie węzeł DOM)
  // opcje: { linkOdmiany: bool = true, przyciskKoszyka: bool = true, bazaZdjec: "./attached_assets/photos/" }
  renderProductCard(wino, stawkaVat, opcje = {}),

  formatujCene(liczba),   // "65,00 zł"
};
```

- Zwracany string zawiera **te same klasy CSS**, co dzisiejsze karty — bundle Tailwinda jest
  zamknięty i nie da się dołożyć nowej klasy utility.
- Zawiera też atrybuty `data-*`, których potrzebują `initFilters()` i `initCart()`:
  `data-id`, `data-name`, `data-category`, `data-price`, `data-promo`, `data-image`.
  **Nie** zawiera `data-price-net` ani `data-discount` — te były martwe i znikają.
  Atrybuty są tu wyłącznie nośnikiem stanu dla już istniejącego kodu filtrów i koszyka;
  źródłem prawdy pozostaje `data/wina.json`.
- `Produkty.formatujCene()` **zastępuje** dotychczasową `formatPrice()` z `main.js` — starą
  funkcję usuwamy, a jej wywołania w `renderCart()` przepinamy. Dwie funkcje formatujące ceny
  rozjechałyby się przy pierwszej zmianie formatu.
- `opcje.przyciskKoszyka: false` służy panelowi: podgląd pokazuje kartę bez działającego
  przycisku „Dodaj".
- `opcje.bazaZdjec` pozwala panelowi wskazać własną ścieżkę do zdjęć.
- Kolejność w `index.html` i na stronach odmian: `produkty.js` **przed** `main.js`, oba z `defer`.

### Decyzje projektowe

1. **Treść odmian jest statyczna, ceny dynamiczne.** Do SEO liczy się unikalna treść, a ta jest
   w HTML. Cena w HTML nie jest potrzebna robotom, a w JSON-ie jest łatwa do zmiany. Strona
   odmiany działa poprawnie także wtedy, gdy `fetch` się nie powiedzie.
2. **Strony powstają per odmiana, nie per wino.** Znamy siedem odmian; asortymentu jeszcze nie.
   Wino w JSON wskazuje odmianę polem `odmiana_slug`, więc jedna strona obsłuży dowolną liczbę
   roczników tej samej odmiany. Gdy pojawi się asortyment, nie trzeba przebudowywać struktury.
3. **Adresy z rozszerzeniem `.html`** (`/wina/souvignier-gris.html`). Ładniejsze `/wina/souvignier-gris`
   wymagałoby zmiany w `wsgi.py`, bo dziś taka ścieżka wpada w fallback i zwraca stronę główną
   ze statusem 200 — czyli duplikat treści dla Google. Do rozstrzygnięcia w `TODO.md` #11.
4. **Strony odmian mają uproszczony nagłówek** (logo + „Nasze wina" + „Sklep" + przełącznik
   motywu) i **pełną stopkę**. Powielanie całej nawigacji z `index.html` w siedmiu plikach
   byłoby siódemką kopii do utrzymania bez builda.
5. **Bez nowych zależności.** Render kart to `template literals` w `main.js`; żadnego frameworka
   ani bundlera (zgodnie z `.ai/GUARDRAILS.md` → „Front-end bez frameworka i bez modułów").
6. **Zdjęcia z osobami są wyłączone z użycia** do czasu potwierdzenia zgód (`TODO.md` #14).
   Rozpoznaje się je po członie `-osoby-` w nazwie pliku.

### Wpływ na obowiązujące reguły (blokada B2 — zgoda NIE została jeszcze udzielona)

Ta zmiana unieważnia dwie rzeczy zapisane wcześniej. **Dopóki w Changelogu tej specyfikacji nie
ma wpisu potwierdzającego zgodę Właściciela, sesja implementująca nie rusza sklepu ani tych
plików** — `GUARDRAILS.md` jest zbiorem reguł nienaruszalnych i sama specyfikacja go nie znosi:

- `.ai/GUARDRAILS.md` → granica #1 („`main.js` NIGDY nie trzyma danych produktów. Źródłem prawdy
  są atrybuty `data-*` w `index.html`") i reguła BLOCK #3 (o sześciu miejscach z ceną) oraz
  decyzja architektoniczna „Dane produktów w HTML zamiast w bazie".
- `.ai/standards/content/product-card.md` — opisuje ręczną kartę produktu, która przestaje istnieć.

Proponowane brzmienie po zmianie: źródłem prawdy jest `data/wina.json`; `main.js` renderuje karty,
ale ich nie definiuje; ceny brutto są jedynymi zapisanymi — netto i rabat są zawsze wyliczane.

## Data Models

### `data/wina.json`

```json
{
  "waluta": "PLN",
  "stawka_vat": 0.23,
  "kategorie": ["Białe", "Czerwone", "Różowe", "Soki"],
  "wina": [
    {
      "id": "souvignier-gris-2024",
      "nazwa": "Souvignier Gris",
      "odmiana_slug": "souvignier-gris",
      "kategoria": "Białe",
      "rocznik": 2024,
      "alkohol": 12.0,
      "pojemnosc_ml": 750,
      "cena_brutto": 65.00,
      "rabat_procent": 0,
      "dostepne": true,
      "opis": "Wytrawne wino o aromatach brzoskwini i cytrusów, ze świeżą kwasowością.",
      "zdjecie": "souvignier-gris-kiscie-02"
    }
  ]
}
```

| Pole | Typ | Wymagane | Uwagi |
|---|---|---|---|
| `id` | string | tak | unikalny; klucz w koszyku. Dwa te same `id` zleją się w jedną pozycję |
| `nazwa` | string | tak | nazwa handlowa na karcie |
| `odmiana_slug` | string | tak | musi odpowiadać plikowi `wina/<slug>.html` |
| `kategoria` | string | tak | jedna z wartości z `kategorie`; patrz uwaga o zgodności niżej |
| `rocznik` | number | nie | pomijany dla soków |
| `alkohol` | number | nie | procent; pomijany dla soków |
| `pojemnosc_ml` | number | tak | 750, 500, 1000… |
| `cena_brutto` | number | tak | **jedyna zapisana cena**; netto liczone przez `/ (1 + stawka_vat)` |
| `rabat_procent` | number | tak | 0 = brak promocji; >0 włącza badge i przekreśloną cenę |
| `dostepne` | boolean | tak | `false` = pozycja znika ze sklepu, zostaje na stronie odmiany |
| `opis` | string | tak | 1–2 zdania na kartę |
| `zdjecie` | string | tak | slug z `attached_assets/photos/` **bez** rozszerzenia i bez `-sm` |

**Reguły wyliczeń** (jedno miejsce w kodzie, `main.js`):

- `netto = cena_brutto / (1 + stawka_vat)`
- `cena_przed_rabatem = cena_brutto / (1 - rabat_procent / 100)` — pokazywana tylko gdy `rabat_procent > 0`
- `promocja = rabat_procent > 0` — zastępuje dawne `data-promo`

**Zgodność kategorii z filtrem.** Dziś filtr to `<select id="category-select">` z zaszytymi
opcjami: `Wszystkie`, `Czerwone`, `Białe`, `Różowe` (dokładnie te napisy, z polskimi znakami),
a `initFilters` porównuje je znak w znak z `card.dataset.category`. Dorzucenie kategorii `Soki`
wymagałoby dziś ręcznej edycji HTML. Dlatego **opcje `<select>` mają być renderowane z tablicy
`kategorie`** — `Wszystkie` jako pierwsza pozycja wstawiana przez JS, reszta z JSON-a. To
usuwa drugie miejsce, w którym trzeba pamiętać o kategoriach.

**Walidacja przy starcie** (`initShop`): brak pliku, błąd składni albo pusta lista → w miejscu
sklepu pokazuje się komunikat „Nie udało się wczytać oferty. Skontaktuj się z nami" z linkiem do
sekcji kontaktu, a błąd ląduje w `console.error`. Strona nie może zostać z pustą sekcją bez wyjaśnienia.
Pozycja z `kategoria` spoza tablicy `kategorie` jest pomijana i zgłaszana w `console.warn` —
literówka w danych nie może wysypać całego sklepu.

### Mapa odmian

| Odmiana | Slug / plik | Kategoria | Zdjęcia bez osób |
|---|---|---|---|
| Souvignier Gris | `souvignier-gris` | Białe | `souvignier-gris-kiscie-01/02`, `souvignier-gris-liscie-01` |
| St. Pepin | `st-pepin` | Białe | `st-pepin-kiscie-01/02`, `st-pepin-winnica-01/02` |
| Vidal Blanc | `vidal-blanc` | Białe | `vidal-blanc-kiscie-01/02/03`, `vidal-blanc-zbiory-01` |
| Seyval Blanc | `seyval-blanc` | Białe | `seyval-blanc-kieliszki-01` |
| Monarch | `monarch` | Czerwone | `monarch-kieliszek-01`, `monarch-butelka-01` |
| Dornfelder | `dornfelder` | Czerwone | `dornfelder-kiscie-01`, `dornfelder-kieliszek-01` |
| Swenson Red | `swenson-red` | Czerwone | `swenson-red-kiscie-01/02` |
| — (soki) | `soki` | Soki | `winnica-butelka-biale-01`, `seyval-blanc-kieliszki-01` |

**Swenson Red** — Właściciel potwierdził 2026-09-02, że wino z tej odmiany jest produkowane.
Strona powstaje jak pozostałe, mimo że pisany opis winnicy jej nie wymienia.

**Soki** dostają **stronę zbiorczą** `wina/soki.html` — nie pochodzą z jednej odmiany, a karta
w sklepie musi mieć dokąd linkować. Strona opisuje soki 100% z białych winogron (bez dodatków)
i wskazuje odmiany, z których powstają. Dzięki temu `odmiana_slug` pozostaje polem wymaganym
dla **każdej** pozycji cennika — bez wyjątków w kodzie i bez martwych linków.

Zdjęcia ogólne: `winnica-panorama-01` (hero), `winnica-budynek-01`, `winnica-rzedy-01`,
`winnica-butelka-biale-01`, `winnica-butelka-czerwone-01`.

### Tytuły i opisy stron odmian

Do wpisania w `<title>` i `<meta name="description">`. Opisy są robocze — wolno je poprawić,
ale każdy musi zostać unikalny i mieścić się w 150–160 znakach.

| Slug | `<title>` | `<meta name="description">` |
|---|---|---|
| `souvignier-gris` | Souvignier Gris — biała odmiana z Winnicy Kielna Góra | Odporna biała odmiana o aromatach brzoskwini i cytrusów, o świeżej kwasowości. Uprawiamy ją na południowym stoku w Kielnarowej pod Rzeszowem. |
| `st-pepin` | St. Pepin — mrozoodporna biała odmiana z Kielnarowej | Hybryda bardzo odporna na mróz, o kwiatowo-miodowym profilu i niskiej kwasowości. Rośnie w naszej winnicy na południowym stoku pod Rzeszowem. |
| `vidal-blanc` | Vidal Blanc — biała odmiana na wina słodkie i lodowe | Gruba skórka i wysoka kwasowość czynią z niej odmianę na wina słodkie i lodowe. Aromaty owoców tropikalnych i melona. Winnica Kielna Góra. |
| `seyval-blanc` | Seyval Blanc — świeże białe wino z Podkarpacia | Hybryda o cytrusowo-ziołowym charakterze, porównywana do lekkiego sauvignon blanc. Uprawiana w Winnicy Kielna Góra pod Rzeszowem. |
| `monarch` | Monarch — czerwona odmiana z Winnicy Kielna Góra | Ciemne jagody dają wina barwne i wyraziste, z nutami czarnej porzeczki. Odmiana odporna na choroby grzybowe, uprawiana w Kielnarowej. |
| `dornfelder` | Dornfelder — soczyste czerwone wino z Kielnarowej | Odmiana znana z owocowych win o miękkich taninach i intensywnej barwie. Uprawiamy ją na jednohektarowej winnicy pod Rzeszowem. |
| `swenson-red` | Swenson Red — mrozoodporna czerwona odmiana | Wysoka odporność na mróz i lekkie, owocowe czerwone wina z nutami malin i wiśni. Winnica Kielna Góra w Kielnarowej pod Rzeszowem. |

### JSON-LD — decyzja

Na stronach odmian idzie **`WebPage` + `BreadcrumbList`**, bez `Product`. Powód: strona opisuje
**odmianę winorośli**, a nie konkretny towar z ceną, a cena celowo nie jest w statycznym HTML
(decyzja projektowa #1). `Product` bez `offers` jest wg wytycznych Google niekompletny, a `Product`
z ceną wymagałby wpisania ceny na stałe w siedmiu plikach — czyli dokładnie tego, co ta zmiana
likwiduje. Na stronie głównej dochodzi `Organization` z nazwą, adresem i logo (adres dopiero po
uzupełnieniu danych kontaktowych, `TODO.md` #9).

## UI / UX

### Sekcja `#sklep` w `index.html`

Markup filtrów zostaje bez zmian. Znika sześć elementów `<article class="product-card">`,
a na ich miejsce wchodzi pusty kontener `<div id="lista-produktow" class="…">`. Karty renderuje
`renderProductCard(wino, ustawienia)` w `main.js`, zachowując **dokładnie te same klasy CSS**,
co obecne karty — bundle Tailwinda jest zamknięty i nie da się dołożyć nowej klasy utility.

Zmiany wobec dzisiejszej karty:
- nazwa wina staje się linkiem do `wina/<odmiana_slug>.html`,
- cena netto, cena sprzed rabatu i badge `-N%` są wyliczane,
- atrybuty `data-price-net` i `data-discount` znikają (były martwe).

Suwak ceny: `min` i `max` ustawiane po wczytaniu danych na podłogę i sufit z `cena_brutto`
(zaokrąglone w dół i w górę do pełnych złotych). Etykiety `#price-min-label` / `#price-max-label`
aktualizowane tak jak dziś.

### Strona odmiany `wina/<slug>.html`

Sekcje, w kolejności: nagłówek uproszczony → zdjęcie tytułowe + nazwa odmiany + krótki lead →
2–3 akapity o odmianie (charakter, aromaty, do czego pasuje) → „Jak uprawiamy ją w Kielnej Górze"
(nawiązanie do stoku południowego, nasadzeń z 2020, zbiorów) → lista cech (te same punkty, co
w kafelku na stronie głównej) → galeria 2–3 zdjęć tej odmiany → blok „Wina z tej odmiany"
(z JSON) → link „Zobacz wszystkie nasze odmiany" → stopka.

Wymagane w `<head>` każdej strony:

```html
<title>Souvignier Gris — biała odmiana z Winnicy Kielna Góra</title>
<meta name="description" content="…150–160 znaków, unikalny dla każdej odmiany…">
<link rel="canonical" href="https://winnicakielnagora.pl/wina/souvignier-gris.html">
<meta property="og:title" content="…"><meta property="og:description" content="…">
<meta property="og:image" content="https://winnicakielnagora.pl/attached_assets/photos/souvignier-gris-kiscie-02.jpg">
<meta property="og:type" content="article">
```

Plus JSON-LD w `<script type="application/ld+json">` — typ i uzasadnienie w sekcji „JSON-LD — decyzja".

**Dostępność i wydajność**: każdy `<img>` ma `alt` po polsku, `loading="lazy"` poza zdjęciem
tytułowym, `width`/`height` dla uniknięcia skoku układu. Miniatury (`-sm`) w kartach i galerii,
wersje 1600 px tylko jako zdjęcia tytułowe.

### Poprawki treści na stronie głównej

| Miejsce | Dziś | Po zmianie |
|---|---|---|
| `#o-nas`, akapit | „rodzinne gospodarstwo… od ponad 15 lat", „gleby wapienne" | winnica w Kielnarowej, 10 km od centrum Rzeszowa, na stoku o południowym nachyleniu; pierwsze nasadzenia 2020, założona 2024 |
| `#o-nas`, liczby | „15+ lat doświadczenia", „12 hektarów", „20+ rodzajów win" | „2020 pierwsze nasadzenia", „1 hektar", „7 uprawianych odmian" |
| Stopka | „produkowane z pasją od 2009 roku", „© 2024" | zgodnie z faktami; rok w stopce aktualizowany |
| `<title>` strony | „WinnicaKielnaGora.pl - Wina z Serca Polski" | nazwa + lokalizacja, np. „Winnica Kielna Góra — wina z Kielnarowej pod Rzeszowem" |
| Zdjęcia (9 grafik AI) | `attached_assets/generated_images/*` | prawdziwe z `attached_assets/photos/` |

Wyjątek: dla **butelek z etykietami** i **wnętrza do degustacji** nie ma zdjęć (`TODO.md` #15).
W tych miejscach zostają grafiki AI, dopóki nie będzie sesji zdjęciowej — z komentarzem w kodzie.

### SEO — pliki w katalogu głównym

- `sitemap.xml` — strona główna + 7 stron odmian, `lastmod` z daty wdrożenia.
- `robots.txt` — `Allow: /` i wskazanie sitemapy.
- W `index.html`: `<link rel="canonical">`, opis meta i Open Graph (dziś jest tylko `<title>`).

## Configuration

Brak zmiennych środowiskowych i brak kroku budowania. Jedyne „ustawienia" to `waluta`,
`stawka_vat` i `kategorie` na górze `data/wina.json`.

Uruchomienie lokalne bez zmian: `python3 -m http.server 5000` w katalogu repo.
**Uwaga:** po tej zmianie strona wymaga serwera — otwarcie `index.html` przez `file://`
zablokuje `fetch` i sklep się nie wczyta.

## Implementation Checklist

Standardy do wstrzyknięcia (sprawdzone w `.ai/standards/index.yml` — wszystkie istnieją):
`content/html-editing`, `frontend/js-conventions`, `frontend/styling`. Przy pracy nad kolorami
dochodzi `frontend/theming`.

**Etap 1 — nie wymaga zdjęcia żadnej blokady**

- [x] Inject standards
- [x] Poprawki faktów w `#o-nas` (Kielnarowa, 1 ha, 2020/2024, 7 odmian), stopce i `<title>`
- [x] Podmiana zdjęć AI na prawdziwe w `index.html` (bez plików z członem `-osoby-`)
- [x] `wina/souvignier-gris.html` — wzorzec dla pozostałych
- [x] `wina/` — St. Pepin, Vidal Blanc, Seyval Blanc, Monarch, Dornfelder, Swenson Red
- [x] `wina/soki.html` — strona zbiorcza soków
- [x] `sitemap.xml`, `robots.txt`, meta, Open Graph, JSON-LD
- [ ] Przegląd w przeglądarce we wszystkich trzech motywach — **do zrobienia przez Właściciela**,
      rozszerzenie Chrome nie było podłączone (sprawdzone inaczej: HTTP 200 dla wszystkich
      adresów, poprawny JSON-LD i XML, 20 testów logiki cen w `tools/test-produkty.js`)

**Etap 2 — mechanizm sklepu (nie wymaga danych; działa na pustym JSON)**

- [x] Aktualizacja `.ai/GUARDRAILS.md` i zastąpienie standardu `content/product-card`
      przez `content/wina-json` — zrobione 2026-09-02 po zgodzie Właściciela
- [x] `data/wina.json` — struktura z pustą tablicą `wina`
- [x] `assets/js/produkty.js` — `policzCeny`, `renderProductCard`, `formatujCene` (kontrakt wyżej)
- [x] `main.js`: `initShop()` — fetch, walidacja, render, obsługa błędu i pustej listy
- [x] `main.js`: opcje `<select>` i zakres suwaka cen z danych (zamyka `TODO.md` #2)
- [x] `main.js`: `initFilters()` i koszyk uruchamiane po renderze
- [x] `index.html`: usunięcie sześciu kart, wstawienie `#lista-produktow`, dodanie `produkty.js`
- [x] `main.js`: `initWineOffer()` — blok „Wina z tej odmiany" na stronach odmian
- [ ] `/sync-standards`

**Etap 2b — po zdjęciu blokady B1**

- [ ] Wprowadzenie realnego asortymentu — panelem z SPEC-002 albo wprost do pliku

**Etap 3 — panel redakcyjny**

- [x] Implementacja wg `.ai/specs/SPEC-002-*` (odblokowuje wprowadzenie asortymentu przez
      Właściciela, czyli zamyka B1)

## Changelog

### 2026-09-02 — wszystkie blokady zdjęte

Właściciel: (1) zatwierdził podział JS na osobne pliki, dopuszczając kolejne, jeśli mają jasno
wydzieloną rolę; (2) potwierdził, że wino **Swenson Red** jest produkowane — blokada B3 zdjęta,
odmiana dostaje stronę jak pozostałe; (3) polecił przygotować **stronę zbiorczą soków**
(`wina/soki.html`), dzięki czemu `odmiana_slug` zostaje polem wymaganym dla każdej pozycji.
Implementacja ruszyła.

### 2026-09-02 — podział JS na dwa pliki (zatwierdzone)

Wydzielenie `assets/js/produkty.js` z `main.js` łamie decyzję architektoniczną „Front-end bez
frameworka i bez modułów" w brzmieniu „jeden plik `main.js`". Zapis w `.ai/GUARDRAILS.md` został przepisany
na wariant wieloplikowy i **zatwierdzony przez Właściciela 2026-09-02**.

Alternatywa, gdyby Właściciel wolał zostać przy jednym pliku: panel kopiuje funkcję renderującą
do siebie — wtedy podgląd karty i sklep rozjadą się przy pierwszej zmianie wyglądu karty, czyli
podgląd przestanie spełniać swoją jedyną funkcję.

### 2026-09-02 — zgoda na zmianę GUARDRAILS (blokada B2 zdjęta)

Właściciel wyraził zgodę na przeniesienie danych produktów z `index.html` do `data/wina.json`
i polecił dostosować `.ai/GUARDRAILS.md` do projektu. Reguły zostały przepisane (granice #1 i #4,
BLOCK #3, #4 i #7, reguły spójności, dwie decyzje architektoniczne), a standard
`content/product-card` zastąpiony przez `content/wina-json`. **B2 nie blokuje już implementacji.**

Dodatkowo: renderowanie karty wydzielone do `assets/js/produkty.js` wraz z kontraktem, żeby panel
redakcyjny (SPEC-002) mógł pokazywać podgląd tym samym kodem, co sklep. `data/wina.json`
powstaje od razu z pustą tablicą — B1 blokuje treść, nie mechanizm.

### 2026-09-02
- Poprawki po recenzji `spec-reviewer`: dodane sekcje „Blokady" (B1–B3), „Materiały źródłowe"
  (opis winnicy i źródła opisów odmian przepisane do specyfikacji, bo `docs/` jest w `.gitignore`),
  zasada postępowania z nieznaną treścią, tytuły i opisy meta dla wszystkich 7 odmian,
  rozstrzygnięcie JSON-LD (`WebPage` + `BreadcrumbList` zamiast `Product`), wymóg renderowania
  opcji filtra z `kategorie`, podział checklisty na etapy wg blokad.
- Domena `winnicakielnagora.pl` potwierdzona przez Właściciela jako docelowa; projekt nie jest
  jeszcze dostępny online.
- Pierwsza wersja specyfikacji.
