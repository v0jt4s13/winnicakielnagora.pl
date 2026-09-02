# Karta produktu w sklepie

Produkty nie mają bazy ani pliku z danymi — **każdy produkt to jeden `<article class="product-card">`
w sekcji `#sklep` w `index.html`**. Dodanie lub zmiana produktu = edycja markupu, nigdy `main.js`.

## Atrybuty `data-*`

| Atrybut | Czyta JS? | Znaczenie |
|---|---|---|
| `data-id` | tak (`initCart`) | unikalny klucz w koszyku — dwa produkty z tym samym `id` zleją się w jedną pozycję |
| `data-name` | tak (`initCart`) | nazwa w koszyku |
| `data-image` | tak (`initCart`) | miniatura w koszyku |
| `data-price` | tak (`initFilters`, `initCart`) | **cena brutto po rabacie**, liczba z kropką, bez „zł" |
| `data-category` | tak (`initFilters`) | musi być dokładnie jedną z wartości przycisków filtra (`Czerwone`, `Białe`, `Różowe`, …) |
| `data-promo` | tak (`initFilters`) | `"true"` / `"false"` — steruje filtrem „tylko promocje" |
| `data-price-net` | **nie** | duplikat ceny netto, utrzymywany ręcznie |
| `data-discount` | **nie** | duplikat wielkości rabatu, utrzymywany ręcznie |

## Zmiana ceny dotyka sześciu miejsc w jednej karcie

1. `data-price` — brutto po rabacie
2. `data-price-net` — `data-price / 1.23`
3. widoczna cena główna (`<span class="text-2xl font-bold …">79.95 zł</span>`)
4. `netto: 65.00 zł` pod ceną
5. przekreślona cena przed rabatem — `data-price / (1 - rabat/100)` — **tylko przy promocji**
6. badge `-15%` w prawym górnym rogu obrazka — **tylko przy promocji**

Plus `data-promo` i `data-discount`. Nic tego nie waliduje — rozjazd zobaczy dopiero klient.

## Promocja vs. produkt bez promocji

```html
<!-- promocja: badge, przekreślona cena, cena główna w text-ring -->
<span class="absolute top-3 right-3 … bg-ring text-primary …">-15%</span>
<span class="text-sm text-muted-foreground line-through">94.06 zł</span>
<span class="text-2xl font-bold text-ring">79.95 zł</span>

<!-- bez promocji: bez badge'a, bez przekreślenia, cena w text-foreground -->
<span class="text-2xl font-bold text-foreground">59.00 zł</span>
```

## Reguły

- **Brutto = netto × 1.23.** VAT 23% jest zaszyty w `renderCart` (`subtotal / 1.23`) i w etykiecie
  koszyka. Inna stawka wymaga zmiany kodu, nie tylko atrybutu.
- **Cena musi mieścić się w 0–100 zł**, inaczej produkt zniknie za filtrem cenowym (zakres jest
  zaszyty w `input[type="range"]` i w `initFilters`). Droższy produkt = najpierw zmiana zakresu.
- **Nowy produkt kopiuj z sąsiedniej karty** tej samej odmiany (promocyjnej lub nie) i podmień
  wartości — to jedyny obowiązujący wzorzec markupu.
- **Nowa kategoria** wymaga też przycisku filtra w `#sklep`; wartość `data-category` musi się
  zgadzać co do znaku.

## Why

Duplikacja ceny w sześciu miejscach to świadomy koszt braku backendu. Skoro nic jej nie pilnuje,
pilnuje jej ten standard — rozjazd między `data-price` a widocznym tekstem już raz wystąpił
(produkt „Chardonnay Premium": `59.00 / 1.23 = 47.97`, a w markupie stoi `netto: 48.00 zł`).
