# Przełącznik słowa „tradycyjne" (`?slowo=`)

## Zakres

- Dodać do `wsgi.py` narzędziowy wariant strony głównej `?slowo=<wariant>`, wzorowany 1:1
  na `?hero=<pora>`: serwer podmienia w `index.html` wystąpienia słowa „tradycyjne"
  i dokłada pasek podglądu z opcjami.
- Warianty: `tradycyjne` (oryginał, no-op), `kraftowe`, `rzemieslicze`.
- **Produkcyjne `/` bez parametru zostaje bez zmian** — zwykły gość widzi „Tradycyjne".
- Pasek renderuje `main.js` wyłącznie, gdy serwer doda `body[data-slowo-kandydaci]` —
  dokładnie jak `data-hero-kandydaci` dla paska kadru.
- `?hero=` i `?slowo=` mają dać się łączyć w jednym adresie; linki w obu paskach zachowują
  drugi parametr.
- Rozszerzyć `tools/test-routing.py` o nowy wariant.
- Nie dodawać zależności. Nie ruszać domyślnej ścieżki `_strona_glowna()`.

## Miejsce zmiany

- **`wsgi.py`**
  - `SLOWA_KANDYDACI = ("tradycyjne", "kraftowe", "rzemieslicze")`.
  - Mapa zamian po **formach faktycznie obecnych** w `index.html`. Dziś jest jedna forma:
    „Tradycyjne" (hero: „Tradycyjne wina z bieszczadzkich stoków"). Mapa trzyma pary
    `(wzorzec, zamiennik)` z zachowaniem wielkości liter:
    ```python
    ZAMIANY_SLOWA = {
        "kraftowe":     [("Tradycyjne", "Kraftowe"),     ("tradycyjne", "kraftowe")],
        "rzemieslicze": [("Tradycyjne", "Rzemieślnicze"), ("tradycyjne", "rzemieślnicze")],
        "tradycyjne":   [],  # wariant oryginalny
    }
    ```
    Gdy Właściciel dopisze do treści inne formy („tradycyjnych", „tradycyjną"…),
    trzeba dodać odpowiadające pary — komentarz w kodzie ma to mówić wprost.
  - Wspólna gałąź narzędziowa w `serve()` dla `path == ""`:
    `if "hero" in request.args or "slowo" in request.args:` → buduje wariant z paskiem
    (`Cache-Control: no-store`, bez `make_conditional`).
  - `_strona_glowna_z_paskiem(pora, slowo)` (rozszerzenie istniejącej funkcji):
    - jeśli `pora` w `HERO_PORY` → wstrzyknięcie kadru jak dziś;
    - jeśli `slowo` w `SLOWA_KANDYDACI` i różne od `tradycyjne` → wykonać zamiany;
      gdy **żadna** para nie trafiła → `500` z jasnym komunikatem (jak przy braku kotwicy
      hero — cichy no-op zafałszowałby podgląd);
    - do `<body>` dokłada `data-slowo-kandydaci="tradycyjne,kraftowe,rzemieslicze"`,
      obok istniejącego `data-hero-kandydaci`, gdy oba parametry są w adresie.
  - Nieznana wartość `?slowo=` (np. `?slowo=1`) → sam pasek, bez podmiany (jak `?hero=1`).

- **`assets/js/main.js`**
  - Wydzielić budowę paska z `initPrzelacznikHero()` do wspólnego helpera (tytuł + opcje
    jako linki + link zamykający) **albo** dodać bliźniaczy `initPrzelacznikSlowa()`
    czytający `document.body.dataset.slowoKandydaci`.
  - Linki opcji: `?slowo=<x>`; jeśli w adresie jest `?hero=<y>` — zachować go
    (i odwrotnie: pasek hero zachowuje `?slowo`). Budować przez `URLSearchParams` na
    `location.search`, nie ręczną konkatenacją.
  - Etykiety: „Tradycyjne", „Kraftowe", „Rzemieślnicze". Tytuł paska: „Słowo w treści".
  - Rejestracja w `DOMContentLoaded` obok `initPrzelacznikHero()`.

- **`assets/css/custom.css`**
  - Reużyć klas `.przelacznik-hero*` albo dodać `.przelacznik-slowo` o tym samym wyglądzie.
  - Gdy oba paski są naraz (`?hero=…&slowo=…`) — rozsunąć w pionie, żeby się nie nakładały
    (drugi pasek wyżej / niżej o własną wysokość). Kolory przez `hsl(var(--…))`.

- **`tools/test-routing.py`**
  - `?slowo=1` → w HTML jest `data-slowo-kandydaci` i pasek.
  - `?slowo=kraftowe` → treść zawiera „Kraftowe wina", nie „Tradycyjne wina".
  - `?slowo=rzemieslicze` → „Rzemieślnicze wina".
  - `?slowo=cokolwiek` → pasek bez podmiany (dalej „Tradycyjne wina").
  - `/` bez parametru → „Tradycyjne wina", brak `data-slowo-kandydaci`.
  - `?hero=noc&slowo=kraftowe` → obie podmiany naraz, oba atrybuty `data-*-kandydaci`.

## Powód

Właściciel waha się między „kraftowe" a „rzemieślnicze" zamiast „tradycyjne" i chce
zobaczyć każdą wersję na żywej stronie przed decyzją — tak samo jak `?hero=` pozwala
obejrzeć każdy kadr hero bez zmiany domyślnego zachowania. Mechanizm jest narzędziem
redakcyjnym, nie funkcją witryny: zwykły odwiedzający nigdy nie zobaczy paska i nic go
to nie kosztuje.

## Weryfikacja

- `python3 tools/dev-server.py --port 5000` — uwaga: pasek składa serwer produkcyjny
  (`wsgi.py`), a `dev-server.py` to `http.server` bez tej logiki. Podgląd `?slowo=`
  sprawdzić na Flasku: `python3 -m flask --app wsgi run --port 8004`.
- `?slowo=kraftowe` → hero „Kraftowe wina z …", pasek „Słowo w treści" widoczny.
- `?slowo=rzemieslicze` → „Rzemieślnicze wina z …".
- `?slowo=1` → pasek, treść bez zmian.
- `/` → „Tradycyjne wina z …", brak paska, brak `data-slowo-kandydaci`.
- `?hero=zachod&slowo=rzemieslicze` → kadr zachód + „Rzemieślnicze", oba paski nie nachodzą
  na siebie; klik opcji w jednym pasku zachowuje wybór z drugiego.
- Konsola bez błędów. `python3 tools/test-routing.py` przechodzi (z nowymi asercjami).
- Cztery motywy: pasek(i) czytelne w `classic`, `modern`, `rustic`, `dark`.

## Status

**Zrobione 2026-09-07.** `wsgi.py` (`SLOWA_KANDYDACI`, `ZAMIANY_SLOWA`,
`_wstrzyknij_slowo`, `_strona_glowna_z_paskiem` + `serve`), `assets/js/main.js`
(`budujPasekPodgladu` — wspólny helper hero+słowo, `initPrzelacznikSlowa`),
`assets/css/custom.css` (`.przelacznik-slowo`), `tools/test-routing.py`
(`sprawdz_slowo`). Sprawdzone na Flasku i w przeglądarce — oba paski, brak nachodzenia,
zachowanie drugiego parametru.

**Aktualizacja 2026-09-07 (później tego dnia).** Właściciel zmienił słowo w hero
z „Tradycyjne" na **„Kraftowe"** (`index.html`). `ZAMIANY_SLOWA`, `SLOWA_KANDYDACI`
(kolejność: `kraftowe` pierwsze = wariant no-op), komunikat 500 i asercje
`sprawdz_slowo` przeliczone od nowego słowa bazowego. `?slowo=tradycyjne` /
`?slowo=rzemieslicze` podmieniają, `?slowo=kraftowe` = no-op. Gdyby słowo bazowe
zmieniło się znów — poprawić te same cztery miejsca (komentarz w `wsgi.py` to mówi).
