# TODO — znane braki i rozjazdy

Rejestr rzeczy, które w kodzie już są niespójne, świadomie niedokończone albo czekają na dane
od Właściciela. To nie jest backlog funkcji. Przeczytaj przed większą zmianą; po zamknięciu
pozycji usuń ją i dopisz regułę do `.ai/standards/` lub `.ai/GUARDRAILS.md`.

Ostatnia aktualizacja: **2026-09-02**.

## Do naprawy

### 1. Rozjazd ceny netto na karcie „Chardonnay Premium"

- **Gdzie**: `index.html`, sekcja `#sklep` — `grep -n 'data-name="Chardonnay Premium"' index.html`
- **Problem**: `data-price="59.00"` → netto `59.00 / 1.23 = 47.97`, a w markupie stoi
  `netto: 48.00 zł` i `data-price-net="48.00"`. Koszyk pokazuje 47.97, karta 48.00.
- **Status**: znika razem z przejściem sklepu na JSON — cena netto będzie wyliczana, nie
  przepisywana. Patrz `.ai/specs/SPEC-001-*`.

### 2. Filtr cenowy ma zaszyty zakres 0–100 zł

- **Gdzie**: `index.html` → `grep -n 'id="price-m' index.html`; `assets/js/main.js` → `initFilters`
  (warunek `max < 100` i reset do `"100"`)
- **Problem**: produkt droższy niż 100 zł zniknie z listy bez żadnego komunikatu.
- **Status**: objęte SPEC-001 — zakres ma być liczony z danych w JSON.

### 3. Martwe atrybuty `data-price-net` i `data-discount`

- **Gdzie**: wszystkie `<article class="product-card">` w `index.html`
- **Problem**: JS ich nie czyta (`grep -n 'dataset\.' assets/js/main.js`) — netto i rabat są
  zduplikowane jako zwykły tekst w markupie.
- **Status**: objęte SPEC-001 — karty przestają być pisane ręcznie.

### 4. VAT 23% zaszyty w dwóch miejscach

- **Gdzie**: `assets/js/main.js` → `renderCart` (`subtotal / 1.23`); `index.html` → etykieta
  „VAT (23%)" w panelu koszyka
- **Co zrobić**: jedna stała na górze `main.js`, etykieta budowana z niej.

### 5. `wsgi.py` nigdy nie zwraca 404

- **Gdzie**: `wsgi.py` → `serve()`
- **Problem**: każda nieznana ścieżka dostaje `index.html` ze statusem 200. Literówka w linku
  albo martwe odwołanie do grafiki nigdy się samo nie ujawni — także dla wyszukiwarek, którym
  taki fallback pokazuje duplikaty strony głównej pod każdym błędnym adresem.
- **Co zrobić**: zwracać 404 dla ścieżek z rozszerzeniem pliku, a fallback zostawić tylko dla
  ścieżek „stronowych". Dochodzi do tego rozstrzygnięcie adresów stron win (patrz #11).

## Do decyzji Właściciela

### 6. Rozjazd treści: odmiany w „Nasze wina" vs. produkty w sklepie

- **Stan**: „Nasze wina" wymienia 7 odmian faktycznie uprawianych, a sklep sprzedaje
  demo-produkty („Cabernet Sauvignon Reserve", „Chardonnay Premium", „Rosé Selection").
- **Status**: kierunek ustalony — sklep ma się budować z zewnętrznego pliku JSON. Brakuje
  samych danych (patrz #10).

### 7. Koszyk i formularz są zaślepkami

- Koszyk to `Map` w pamięci — znika po odświeżeniu strony.
- Formularz kontaktowy robi `preventDefault()` + `alert()`, nie wysyła nic; przycisk płatności
  też kończy się `alert()`.
- **Pytanie**: czy i kiedy dokładamy backend (wysyłka maila, trwały koszyk, płatności)? To
  zadanie rozmiaru **L**.
- **Uwaga dla agentów**: `alert()` zawiesza automatyzację przeglądarki — tych przycisków nie
  klikaj przez Chrome MCP.

### 8. `dist/public` — build, którego nie ma

- **Gdzie**: `wsgi.py` → `STATIC_CANDIDATES`
- **Stan**: kod preferuje `dist/public`, ale wdrożenie nie ma kroku budowania, więc na produkcji
  serwowany jest katalog repo. Gałąź `dist/public` jest martwa.
- **Pytanie**: dodajemy build, czy usuwamy tę gałąź z `wsgi.py`?

## Brakujące dane do strony

Bez tych informacji na stronie zostają atrapy. Nie da się ich zgadnąć ani wyprowadzić
z materiałów w `docs/`.

### 9. Dane kontaktowe

Sekcja `#kontakt` i stopka podają dziś adres **ul. Winnicza 12, 38-700 Ustrzyki Dolne**,
telefon **+48 123 456 789** i e-mail **kontakt@winnicapodkarpacka.pl** — wszystko zmyślone.
Potrzebne: dokładny adres (wiadomo tylko, że Kielnarowa), telefon, e-mail, godziny otwarcia,
ewentualnie NIP i dane do faktury, jeśli ma być sprzedaż.

### 10. Asortyment i cennik do `data/wina.json`

Potrzebne dla każdej pozycji: nazwa handlowa, kategoria (białe / czerwone / różowe / sok),
rocznik, zawartość alkoholu, pojemność, cena brutto, ewentualny rabat, opis, dostępność.
Dotyczy też **soków winogronowych** — z opisu winnicy wynika, że są w ofercie; do ustalenia,
czy trafiają do cennika jako osobna kategoria, czy tylko do treści.

### 11. Adresy stron poszczególnych win

Strony win mają być statycznymi plikami HTML (SEO). Do rozstrzygnięcia, czy adres ma wyglądać
jak `/wina/souvignier-gris.html`, czy jak `/wina/souvignier-gris` — ta druga forma wymaga
dopisania w `wsgi.py` próby dołożenia `.html` przed fallbackiem (patrz #5).

### 12. Svenson Red — czy ta odmiana jest uprawiana?

Jest folder ze zdjęciami i karta na stronie, ale opis winnicy
(`docs/materialy-do-wykorzystania/zbiory_i_winnica/Winnica Kielna Góra.txt`) wymienia tylko
Souvignier Gris, St. Pepin, Vidal Blanc, Seyval Blanc, Monarch i Dornfelder.

### 13. Wydarzenia i degustacje

Sekcja `#wydarzenia` ma trzy zmyślone terminy (15 i 22 listopada 2025, 6 grudnia 2025) z cenami
120–180 zł/os. Do decyzji: realne terminy i ceny, czy przepisanie sekcji na ofertę „na
zamówienie" bez dat, której nie trzeba aktualizować co miesiąc.

## Materiały

### 14. Zgody na wizerunek

Część zdjęć pokazuje rozpoznawalne osoby przy zbiorach i gości winnicy. W nazwach plików
w `attached_assets/photos/` mają one człon **`-osoby-`**. Do czasu potwierdzenia zgód
na stronie używamy wyłącznie kadrów bez tego członu.

### 15. Brakujące ujęcia

W materiałach nie ma zdjęć **butelek z etykietami**, **wnętrza do degustacji** ani ujęcia
budynku innego niż `winnica-budynek-01`. Strona pokazuje dziś w tych miejscach grafiki AI
(`attached_assets/generated_images/`). Potrzebna sesja zdjęciowa albo zgoda na dalsze
korzystanie z grafik zastępczych.

### 16. Filmy nie są wykorzystane

W `docs/` leży 12 filmów 1080p (3–34 s, 6–74 MB). Nie są nigdzie użyte i nie ma decyzji, czy
mają być (tło sekcji hero, galeria, czy wcale). Kompresję zrobi `ffmpeg`, jest zainstalowany.

## Higiena repo

### 17. `.claude/skills/` i `.claude/agents/` są w `.gitignore`

Po świeżym klonie nie ma komend `/…` ani subagentów. Odtworzyć powinien je
`t-shirt-size-install.sh`, ale **instalator kopiuje z katalogów `skills/` i `agents/`, których
w repo nie ma** — dziś jedyna kopia frameworka to lokalne `.claude/`. Do rozstrzygnięcia:
commitować `.claude/`, czy dodać katalogi źródłowe.
