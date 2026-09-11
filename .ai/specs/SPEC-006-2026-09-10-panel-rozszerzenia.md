---
title: Rozszerzenia panelu redakcyjnego
date: 2026-09-10
status: draft
---

# SPEC-006: Rozszerzenia panelu redakcyjnego

## Cel

Rozszerzyć panel redakcyjny o cztery funkcjonalności:
1. Wyświetlanie identyfikatora (ID) produktu w liście pozycji
2. Dodanie pola „rodzaj" do pozycji (wino: musujące, wytrawne, półsłodkie)
3. Przełącznik lokalizacji dla wydarzeń (sekcja #wydarzenia vs #noclegi)
4. Wielowartościowe zdjęcia dla wydarzeń z galerią i stronicowaniem

## Zmiany w strukturze danych

### `data/wina.json` — nowe pole w obiekcie pozycji

Każdy obiekt w `wina.json` zyska nowe pole:

```json
{
  "id": "cabernet-2020",
  "nazwa": "Cabernet Sauvignon 2020",
  "rodzaj": "wytrawne",  // NOWE: enum [musujące, wytrawne, półsłodkie]
  "kategoria": "Czerwone",
  ...
}
```

**Reguły:**
- `rodzaj` jest **opcjonalne** — także w formularzu panelu, nie tylko na poziomie danych
  (decyzja z 2026-09-11: soki i inne pozycje niebędące winem nie mają rodzaju, wymuszanie
  wyboru na formularzu soku było błędem)
- Jeśli ustawione, musi być jedną z trzech wartości: `"musujące"`, `"wytrawne"`, `"półsłodkie"`
  (walidacja po stronie serwera i przeglądarki dopuszcza tylko te trzy albo brak pola)
- Wyświetla się w karcie produktu pod kategorią (obok, inny wiersz)
- Filtr sklepu NIE zmienia się — filtruje się dalej tylko po kategorii

### `data/wydarzenia.json` — zmiana struktury zdjęć i nowe pole lokalizacji

```json
{
  "id": "degustacja-wrzesien",
  "tytul": "Degustacja winnicy",
  "tresc": "...",
  "data_od": "2026-09-20",
  "data_do": "2026-09-20",
  "zdjecia": [
    "degustacja-2026-09.jpg",
    "degustacja-2026-09-2.jpg"
  ],  // ZMIENIONE: z `zdjecie` (string) na `zdjecia` (array)
  "wyswietl_w": "wydarzenia",  // NOWE: enum [wydarzenia, noclegi]
  "data_publikacji_od": "2026-09-01"
}
```

**Reguły:**
- `zdjecia` to tablica stringów (ścieżki do plików), może być pusta
- `wyswietl_w` jest obligatoryjne; radio button w panelu:
  - `"wydarzenia"` → wyświetli się w sekcji #wydarzenia (domyślnie)
  - `"noclegi"` → wyświetli się w sekcji #noclegi (gdzie?)
- Pierwsza pozycja w tablicy `zdjecia` będzie użyta jako okładka (miniatura)

**Migracja:** istniejące wpisy mają `zdjecie` (string) → konwertuje się na `zdjecia: [zdjecie]` przy ładowaniu; pole `wyswietl_w` dostanie wartość domyślną `"wydarzenia"`.

## Zmiany w panelu redakcyjnym (`tools/panel/`)

### 1. Lista pozycji — wyświetl ID

`panel.html` → sekcja `#lista` — każdy `<li>` będzie wyświetlać ID obok nazwy:

```html
<li data-indeks="0">
  <span class="nazwa">Cabernet Sauvignon 2020</span>
  <span class="meta id">cabernet-2020</span>  <!-- NOWE: ID produktu -->
  <span class="meta">Czerwone</span>
  <span class="meta cena">49,99 zł</span>
  ...
</li>
```

**Implementacja:**
- W `renderLista()` — dodaj wiersz z `wino.id` (escaped)
- Style w `panel.css` — `.meta.id` dostaje inny kolor (szary, mniejszy font) — to tylko label

### 2. Formularz pozycji — pole „rodzaj"

W `panel.html` → formularz `#formularz` dodaj blok po polu kategoria:

```html
<label>Rodzaj
  <select name="rodzaj" required></select>
  <small>Typologia wina.</small>
</label>
```

**Implementacja:**
- `panel.js` → `renderFormularz()` — população select z trzema opcjami
- Walidacja: `bledyPozycji()` — sprawdź czy `rodzaj` jest jedną z trzech wartości
- Zapis: `zbierzFormularz()` — przepisz wartość do `wino.rodzaj`
- Podgląd: `renderProductCard()` w `assets/js/produkty.js` NIE pokazuje rodzaju — to zmiana poza panelem (index.html)

### 3. Formularz wydarzeń — radio „wyświetl w"

W `panel.html` → formularz `#formularz-wydarzenia` dodaj blok:

```html
<fieldset>
  <legend>Wyświetl w</legend>
  <label class="pole-radio">
    <input type="radio" name="wyswietl_w" value="wydarzenia" required>
    <span>Sekcja Wydarzenia</span>
  </label>
  <label class="pole-radio">
    <input type="radio" name="wyswietl_w" value="noclegi" required>
    <span>Sekcja Noclegi</span>
  </label>
</fieldset>
```

**Implementacja:**
- `panel.js` → `renderFormularzWydarzenia()` — ustaw radio na obecną wartość
- Walidacja: `bledyWydarzenia()` — sprawdź czy `wyswietl_w` jest `"wydarzenia"` lub `"noclegi"`
- Zapis: `zbierzFormularzWydarzenia()` — przepisz wartość

### 4. Galeria zdjęć dla wydarzenia

Dodaj blok pod formularzem `#formularz-wydarzenia`:

```html
<details class="galeria-wydarzenia" open>
  <summary>Galeria zdjęć do wydarzenia</summary>
  <div class="galeria-wydarzenia-filtry">
    <label>Katalog
      <select id="galeria-wydarzenia-katalog"></select>
    </label>
    <span id="galeria-wydarzenia-zaznaczenie" class="podpowiedz"></span>
  </div>
  <div id="galeria-wydarzenia-grid" class="galeria-grid"></div>
  
  <div class="galeria-wydarzenia-akcje">
    <button type="button" id="dodaj-zdjecia-do-wydarzenia" class="przycisk">Dodaj zaznaczone do wydarzenia</button>
  </div>
  
  <div id="galeria-wydarzenia-paginacja" class="paginacja"></div>
</details>

<!-- sekcja poniżej formularza pokazuje aktualne zdjęcia wydarzenia -->
<div id="zdjecia-wydarzenia" class="zdjecia-wydarzenia" hidden>
  <h4>Zdjęcia w tym wydarzeniu</h4>
  <ul id="lista-zdjecialb-wydarzenia" class="lista-zdjecialb"></ul>
</div>
```

**Implementacja:**
- `galeriaWydarzenia` — stan lokalny: zaznaczone pliki dla bieżącego wydarzenia, aktualny katalog, numer strony
- `renderGaleriaWydarzenia()` — wyświetl 16 zdjęć bieżącej strony
- `renderPaginacjaWydarzenia()` — guziki/linki do zmian strony
- Kliknięcie checkbox-a — dodaj/usuń z lokalnego zaznaczenia (nie z `zdjecia` w danych)
- Kliknięcie „Dodaj zaznaczone" — skopiuj ścieżki do `wydarzenia[wybraneWydarzenie].zdjecia`, wyczyść zaznaczenie, re-render listy aktualnych zdjęć
- Obok listy aktualnych zdjęć — button „Usuń" dla każdego zdjęcia

**Opcja:** czy obok każdego zdjęcia w liście aktualnych ma być button "usuń" czy "przesunąć wyżej/niżej"? Zakładam: usunąć (proste) i tyle.

## Zmiany na głównej stronie (`index.html`)

### Wyświetlanie „rodzaju" w karcie produktu

Karta w sekcji `#sklep` — pod kategorią dodaj nowy wiersz:

```html
<p class="kategoria-rodzaj">
  <span class="etykieta">Kategoria:</span>
  <span class="wartosc">Czerwone</span>
  <span class="rodzaj-badge">wytrawne</span>
</p>
```

**Implementacja:**
- `assets/js/produkty.js` → `renderProductCard()` — wyświetl `wino.rodzaj` w specjalnym badge-u
- Styl w `assets/css/custom.css` — `.rodzaj-badge` (mały, odróżniony od kategorii)

### Wyświetlanie wydarzeń w sekcji #noclegi (jeśli `wyswietl_w === "noclegi"`)

Jeśli wydarzenie ma `wyswietl_w: "noclegi"` — pojawia się w sekcji `#noclegi` (nie wiadomo jeszcze gdzie dokładnie; czekaj na wskazówki).

## Zadania implementacyjne

1. **Migracja danych** — serwer (`wsgi.py` / `cennik.py` / `wydarzenia.py`) konwertuje stare formaty przy ładowaniu
2. **Panel — lista pozycji** — ID do odczytu w liście
3. **Panel — formularz pozycji** — pole rodzaj (select)
4. **Panel — formularz wydarzeń** — radio wyswietl_w + galeria zdjęć + stronicowanie
5. **Główna strona — karta produktu** — wyświetl rodzaj
6. **Główna strona — sekcja noclegi** — wyświetl wydarzenia z `wyswietl_w === "noclegi"` (szczegóły po wyjaśnieniu)
7. **Walidacja** — sekcje po stronie serwera (`cennik.py`, `wydarzenia.py`)

## Backlog — do wyjaśnienia

✓ **Gdzie dokładnie wyświetlić treść i zdjęcia wydarzenia w sekcji #noclegi?** — treść **zamiennie** z aktualną treścią karty (tekst wydarzenia zamiast tekstury winnicy), zdjęcia wyświetlają się **poniżej karty rezerwacji Booking**.

✓ **Czy Nocleg może mieć wiele wydarzeń** — tylko **jedno w tym samym czasie**. Jeśli kilka się pokrywa, wyświetla się aktualnie trwające (lub przyszłe) z najwcześniejszą datą. Logika będzie po stronie serwera (funkcja `wydarzenia.aktywne()` już filtruje).

✓ **Czy starsze wpisy (brak pola `rodzaj`) mają dostać wartość domyślną** — **nie**. Brak pola `rodzaj` powoduje jedynie, że nazwa rodzaju się nie wyświetla. Zapisanie pozycji bez rodzaju nie jest błędem — pole jest opcjonalne, także w formularzu panelu (patrz zmiana z 2026-09-11 w sekcji wyżej — soki nie mają rodzaju i formularz nie może tego wymuszać).

## Changelog

### 2026-09-11
- `rodzaj` zmienione z obowiązkowego na opcjonalne w formularzu panelu — sok winogronowy
  (kategoria „Soki") nie ma rodzaju wina i nie powinien być blokowany walidacją

### 2026-09-10
- Wstępna specyfikacja
