# TODO — znane braki i rozjazdy

Lista wykryta przy przeglądzie kodu **2026-09-02**. To nie jest backlog funkcji, tylko rejestr
rzeczy, które w kodzie już są niespójne albo świadomie niedokończone. Przeczytaj przed większą
zmianą; po naprawie usuń pozycję i dopisz regułę do `.ai/standards/` lub `.ai/GUARDRAILS.md`.

## Do naprawy

### 1. Rozjazd ceny netto na karcie „Chardonnay Premium"

- **Gdzie**: `index.html`, sekcja `#sklep` — `grep -n 'data-name="Chardonnay Premium"' index.html`
- **Problem**: `data-price="59.00"` → netto `59.00 / 1.23 = 47.97`, a w markupie stoi
  `netto: 48.00 zł` i `data-price-net="48.00"`. Koszyk pokazuje 47.97, karta 48.00.
- **Co zrobić**: zdecydować, która liczba jest prawdziwa (netto czy brutto), i wyrównać
  pozostałe. Pozostałe karty są spójne (65.00 × 1.23 = 79.95, 42.00 × 1.23 = 51.66).

### 2. Filtr cenowy ma zaszyty zakres 0–100 zł

- **Gdzie**: `index.html` → `grep -n 'id="price-m' index.html`; `assets/js/main.js` → `initFilters`
  (warunek `max < 100` i reset do `"100"`)
- **Problem**: produkt droższy niż 100 zł zniknie z listy bez żadnego komunikatu.
- **Co zrobić**: albo wyliczać zakres z `data-price` wszystkich kart przy starcie, albo
  podnieść limit i zapisać go w jednym miejscu (dziś jest w czterech).

### 3. Martwe atrybuty `data-price-net` i `data-discount`

- **Gdzie**: wszystkie `<article class="product-card">` w `index.html`
- **Problem**: JS ich nie czyta (`grep -n 'dataset\.' assets/js/main.js`) — netto i rabat są
  zduplikowane jako zwykły tekst w markupie. Duplikaty rozjeżdżają się po cichu (patrz #1).
- **Co zrobić**: albo zacząć z nich renderować cenę netto i badge w JS, albo je usunąć
  i zostawić sam tekst. Dziś utrzymujemy jedno i drugie.

### 4. VAT 23% zaszyty w dwóch miejscach

- **Gdzie**: `assets/js/main.js` → `renderCart` (`subtotal / 1.23`); `index.html` → etykieta
  „VAT (23%)" w panelu koszyka
- **Co zrobić**: przy zmianie stawki trzeba ruszyć oba. Docelowo jedna stała na górze `main.js`
  i etykieta budowana z niej.

### 5. `wsgi.py` nigdy nie zwraca 404

- **Gdzie**: `wsgi.py` → `serve()`
- **Problem**: każda nieznana ścieżka dostaje `index.html` ze statusem 200. Literówka w linku
  albo martwe odwołanie do grafiki nigdy się samo nie ujawni (również dla wyszukiwarek).
- **Co zrobić**: zwracać 404 dla ścieżek z rozszerzeniem pliku, a fallback zostawić tylko dla
  ścieżek „stronowych". Wymaga decyzji — dziś fallback jest jedynym routingiem.

## Do decyzji Właściciela

### 6. Rozjazd treści: odmiany w „Nasze wina" vs. produkty w sklepie

- **Gdzie**: sekcje `#nasze-wina` i `#sklep` w `index.html`
- **Stan**: „Nasze wina" opisuje odmiany hybrydowe faktycznie uprawiane (Souvignier Gris,
  St. Pepin, Seyval Blanc), a sklep dalej sprzedaje demo-produkty „Cabernet Sauvignon Reserve",
  „Chardonnay Premium", „Rosé Selection".
- **Pytanie**: czy sklep ma zostać przepisany na realny asortyment, czy pozostaje wersją
  demonstracyjną?

### 7. Koszyk i formularz są zaślepkami

- Koszyk to `Map` w pamięci — znika po odświeżeniu strony.
- Formularz kontaktowy robi `preventDefault()` + `alert()`, nie wysyła nic; przycisk płatności
  też kończy się `alert()`.
- **Pytanie**: czy i kiedy dokładamy backend (wysyłka maila, trwały koszyk, płatności)? To
  zadanie rozmiaru **L** — dokłada projektowi zależność, której świadomie dziś nie ma.
- **Uwaga dla agentów**: `alert()` zawiesza automatyzację przeglądarki — tych przycisków nie
  klikaj przez Chrome MCP.

### 8. `dist/public` — build, którego nie ma

- **Gdzie**: `wsgi.py` → `STATIC_CANDIDATES`
- **Stan**: kod preferuje `dist/public`, ale wdrożenie nie ma kroku budowania, więc na produkcji
  serwowany jest katalog repo. Gałąź `dist/public` jest martwa.
- **Pytanie**: dodajemy build, czy usuwamy tę gałąź z `wsgi.py`?

## Higiena repo

### 9. `.claude/skills/` i `.claude/agents/` są w `.gitignore`

Po świeżym klonie nie ma komend `/…` ani subagentów. Odtworzyć powinien je
`t-shirt-size-install.sh`, ale **instalator kopiuje z katalogów `skills/` i `agents/`, których
w repo nie ma** — dziś jedyna kopia frameworka to lokalne `.claude/`. Do rozstrzygnięcia:
commitować `.claude/`, czy dodać katalogi źródłowe.

### 10. `.DS_Store` nie jest ignorowany

Plik leży w katalogu repo i nie ma go w `.gitignore` — łatwo go przypadkiem zacommitować.
Dopisać `.DS_Store` do `.gitignore`.
