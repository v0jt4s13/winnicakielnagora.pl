# Asortyment i ceny w `data/wina.json`

`data/wina.json` jest **jedynym** źródłem prawdy o tym, co i za ile jest w sklepie.
`index.html` nie zawiera kart produktów; `assets/js/main.js` je renderuje, ale nie definiuje.

## Zapisujemy tylko brutto

```json
{ "cena_brutto": 65.00, "rabat_procent": 10 }
```

Wszystko inne wylicza `main.js`, w jednym miejscu:

- `netto = cena_brutto / (1 + stawka_vat)`
- `cena_przed_rabatem = cena_brutto / (1 - rabat_procent / 100)` — pokazywana tylko gdy rabat > 0
- `promocja = rabat_procent > 0`

**Nigdy** nie zapisuj ceny netto, kwoty rabatu ani ceny sprzed rabatu jako osobnego pola i nie
wpisuj żadnej z nich do HTML-a. Wcześniej cena występowała w sześciu miejscach jednej karty
i rozjechała się po cichu — ten standard istnieje właśnie po to.

## Wymagane pola pozycji

`id` (unikalny, klucz koszyka) · `nazwa` · `odmiana_slug` · `kategoria` · `pojemnosc_ml` ·
`cena_brutto` · `rabat_procent` · `dostepne` · `opis` · `zdjecie`.
Opcjonalne: `rocznik`, `alkohol` (pomijane dla soków).

- `kategoria` musi być jedną z wartości tablicy `kategorie` w tym samym pliku — filtr sklepu
  buduje z niej swoje opcje, więc nowa kategoria nie wymaga zmian w HTML.
- `odmiana_slug` musi wskazywać istniejący plik `wina/<slug>.html`.
- `zdjecie` to slug z `attached_assets/photos/` **bez** rozszerzenia i bez `-sm`; wariant
  miniatury dokłada kod.
- `dostepne: false` usuwa pozycję ze sklepu, ale **nie** ze strony odmiany — zaindeksowany
  adres ma dalej działać.

## Odporność na błędy w danych

- Brak pliku, zła składnia albo pusta lista → komunikat w miejscu sklepu z linkiem do kontaktu
  plus `console.error`. Nigdy pusta sekcja bez wyjaśnienia.
- Pozycja z nieznaną `kategoria` → pomijana i zgłoszona w `console.warn`. Literówka w danych
  nie może wysypać całego sklepu.

## Edycja

Plik zmienia się **panelem redakcyjnym** (`tools/panel/`, tylko `127.0.0.1`) albo ręcznie
w edytorze tekstu. Po zmianie: commit i wdrożenie — nie ma edycji „na żywo" na serwerze.

## Why

Cennik zmienia się częściej niż kod i zmienia go osoba nietechniczna. Trzymanie go w jednym
pliku danych sprawia, że zmiana ceny to jedna liczba, a nie sześć miejsc w markupie.
