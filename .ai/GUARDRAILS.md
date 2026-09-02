# GUARDRAILS

> Nienaruszalne reguły projektu. Obowiązują każdego — człowieka i agenta AI.
>
> Ten plik nie opisuje struktury projektu (to `AGENTS.md`) ani wzorców kodu
> (to `.ai/standards/`). Tu są **granice, których się nie przekracza**.

## Absolute prohibitions

### STOP — immediate revert

Naruszenie = natychmiastowy revert, bez dyskusji.

1. **NEVER** commit secrets (klucze API, hasła, tokeny) do repozytorium — zmienne środowiskowe
   albo menedżer sekretów. Dziś projekt nie ma ani jednego sekretu i tak ma zostać.
2. **NEVER** wstawiaj do repo danych osobowych (maile, telefony, nazwiska klientów) — witryna
   jest w całości publiczna, każdy plik w repo trafia na produkcję.
3. **NEVER** edytuj `assets/css/style.css` — to zbudowany artefakt Tailwinda bez źródeł w repo.
   Ręczna edycja jest nie do odtworzenia i nie do przeglądu (plik ma jedną linię).

> Klasyczne reguły o PII w bazie i o SQL injection **nie mają tu zastosowania** — projekt nie ma
> bazy, backendu ani formularza, który cokolwiek wysyła. Jeśli kiedyś powstaną (zadanie rozmiaru
> **L**), dopisz je tutaj, zanim powstanie pierwszy endpoint.

### BLOCK — do not merge without fix

Naruszenie = poprawa przed scaleniem.

1. **NEVER** dodawaj zmiennej CSS tylko do jednego motywu — każda nowa zmienna musi trafić do
   `classic`, `modern` **i** `rustic` w `themeStyles` (`assets/js/main.js`). `setTheme` ustawia
   style inline i ich nie czyści, więc brak zmiennej w jednym motywie zostawia po przełączeniu
   wartość z poprzedniego. Patrz `.ai/standards/frontend/theming.md`.
2. **NEVER** koduj kolorów na sztywno w `assets/css/custom.css` — zawsze `hsl(var(--nazwa))`,
   inaczej element wypada z systemu motywów.
3. **NEVER** zapisuj ceny netto, ceny sprzed rabatu ani kwoty rabatu jako osobnej danej —
   jedyną zapisaną ceną jest `cena_brutto` w `data/wina.json`, reszta jest **wyliczana**
   w `assets/js/main.js`. Patrz `.ai/standards/content/wina-json.md`.
4. **NEVER** wpisuj produktu na stałe w `index.html` ani w kod JS — nowe wino, sok, cena
   i dostępność to wyłącznie wpis w `data/wina.json`.
5. **NEVER** przeformatowuj `index.html` przy okazji innej zmiany — jeden plik jest jedyną kopią
   treści witryny, a duży diff jest nie do przejrzenia.
6. **NEVER** dodawaj zależności (Python, npm, CDN) bez zgody Właściciela — brak zależności jest
   tu decyzją, nie zaniedbaniem.
7. **NEVER** wystawiaj panelu redakcyjnego poza `127.0.0.1` i nigdy nie wdrażaj go na produkcję —
   panel zapisuje pliki na dysku i nie ma żadnego uwierzytelniania. Patrz
   `.ai/specs/SPEC-002-*` oraz decyzja architektoniczna „Panel redakcyjny poza aplikacją produkcyjną".

## Decision priorities

Gdy wartości są w konflikcie, rozstrzyga ta kolejność:

1. **Poprawność treści publicznej** — to strona firmowa; błędna cena, nieistniejąca odmiana albo
   martwy link są kosztowniejsze niż brzydki kod.
2. **Stabilność wyglądu we wszystkich trzech motywach** — złamany motyw widzi każdy odwiedzający.
3. **Czytelność diffu w `index.html`** — jedyna kontrola jakości, jaką ma tu recenzent.
4. **Brak nowych zależności** — projekt utrzymuje się sam dzięki temu, że nic nie wymaga budowania.
5. **Elegancja kodu** — ostatnia, nie pierwsza.

## Architectural boundaries

1. `data/wina.json` → **JEDYNE** źródło prawdy o asortymencie i cenach. `index.html` nie zawiera
   kart produktów, `assets/js/main.js` je renderuje, ale nie definiuje.
2. `assets/css/custom.css` → **NIGDY** nie duplikuje klas z bundla Tailwinda; dopisuje tylko to,
   czego w bundlu nie ma.
3. `wsgi.py` → **NIGDY** nie dostaje logiki biznesowej ani możliwości zapisu na dysk. To serwer
   plików statycznych; wszystko inne jest zadaniem rozmiaru **L** i wymaga decyzji Właściciela.
4. `tools/` → skrypty uruchamiane ręcznie na maszynie lokalnej (panel redakcyjny, optymalizacja
   zdjęć). **NIGDY** nie są częścią wdrożenia i nie mogą być importowane przez `wsgi.py`.
5. `attached_assets/` i `assets/` → jedyne miejsca na grafiki; ścieżki zawsze względne.

## Consistency rules

1. Dodajesz zmienną CSS → **ZAWSZE** do wszystkich trzech motywów w `themeStyles`.
2. Zmieniasz cenę → **ZAWSZE** tylko `cena_brutto` w `data/wina.json`. Netto, kwota rabatu
   i cena sprzed rabatu są wyliczane; nie zapisuj ich nigdzie.
3. Dodajesz pozycję do `data/wina.json` → **ZAWSZE** unikalne `id`, `kategoria` z listy
   `kategorie` w tym samym pliku i `odmiana_slug` wskazujący na istniejący plik
   `wina/<slug>.html`.
4. Dodajesz kategorię → **ZAWSZE** do tablicy `kategorie`; filtr w sklepie buduje z niej swoje
   opcje, więc nic nie trzeba zmieniać w HTML.
5. Dodajesz odmianę → **ZAWSZE** kafelek w `#nasze-wina` **i** strona `wina/<slug>.html`
   **i** wpis w `sitemap.xml`. Odmiana bez własnej strony jest niewidoczna dla wyszukiwarek.
6. Dodajesz sekcję z `id` → **ZAWSZE** pozycja w nawigacji desktopowej i mobilnej
   (`data-scroll="id-sekcji"`), jeśli ma być osiągalna z menu.
7. Dodajesz zachowanie w JS → **ZAWSZE** jako `initX()` zarejestrowane w `DOMContentLoaded`.
8. Dodajesz ikonę → **ZAWSZE** jako `<symbol id="icon-…">` w ukrytym `<svg>` na początku `<body>`,
   używana przez `<use href="#icon-…">`.

## Allowed exceptions

1. **`alert()` w `initCart` i `initContactForm`** — świadome zaślepki demo, dopóki nie ma backendu.
   Nie rozszerzamy wzorca na nowy kod i pamiętamy, że blokują automatyzację przeglądarki.
2. **Koszyk w pamięci (`Map`), znikający po odświeżeniu** — świadomy stan demo, nie błąd.
3. **Panel redakcyjny zapisuje pliki bez logowania** — dopuszczalne wyłącznie dlatego, że
   nasłuchuje na `127.0.0.1` i nigdy nie jest wdrażany. Poza tym jednym miejscem żaden kod
   w tym projekcie nie zapisuje niczego na dysk.

## Definition of "done"

Zmiana jest gotowa dopiero, gdy:

- [ ] Strona otwarta lokalnie (`python3 -m http.server 5000`) pokazuje zmianę tak, jak zaplanowano
- [ ] Sekcja obejrzana we **wszystkich trzech motywach** (`classic`, `modern`, `rustic`)
- [ ] Konsola przeglądarki bez błędów
- [ ] Przy zmianach w sklepie: filtry (kategoria, zakres cen, „tylko promocje") i koszyk
      (dodanie, +/−, podsumowanie netto / VAT / razem) działają
- [ ] Diff dotyczy wyłącznie fragmentu, którego dotyczyło zadanie
- [ ] W odpowiedzi napisane, co sprawdzono i czego sprawdzić się nie dało
- [ ] Nowa reguła, która wyszła w trakcie pracy, trafiła do `.ai/standards/` (`/sync-standards`)
      albo do tego pliku; nowy znany brak — do `TODO.md`
- [ ] Spec (jeśli istnieje) ma zaktualizowaną sekcję `## Implementation Checklist`

> Nie ma lintera, type-checkera ani testów. Podgląd w przeglądarce jest jedynym dowodem.

## Architectural decisions

### Brak kroku budowania

- **Wybór**: Tailwind leży w repo jako gotowy, zminifikowany `assets/css/style.css`; nie ma
  `package.json`, `tailwind.config` ani źródeł.
- **Dlaczego**: witryna ma się utrzymywać latami bez łańcucha narzędzi — nic nie może się
  „zepsuć przy buildzie", bo buildu nie ma.
- **Konsekwencja**: klasa Tailwinda spoza bundla nie zadziała i nie da się jej dobudować.
  Nowe style piszemy w `custom.css`. Nie proponuj przywracania builda jako „porządków" —
  to zadanie **L** i decyzja Właściciela.

### Dane produktów w pliku JSON, nie w HTML i nie w bazie

- **Wybór**: asortyment i ceny żyją w `data/wina.json`; `main.js` pobiera go przez `fetch`
  i renderuje karty sklepu. Decyzja Właściciela z 2026-09-02, zastępuje wcześniejszy zapis
  o danych zaszytych w `index.html`.
- **Dlaczego**: cennik zmienia się częściej niż kod, a wcześniej jedna zmiana ceny wymagała
  poprawienia sześciu miejsc w markupie — i już raz się rozjechały. Baza wymagałaby backendu,
  którego projekt nie ma.
- **Konsekwencja**: `index.html` nie zawiera kart produktów. Jedyną zapisaną ceną jest
  `cena_brutto`; netto i rabat są wyliczane. Sklep wymaga serwera HTTP — otwarcie
  `index.html` przez `file://` zablokuje `fetch`. Treść sklepu nie jest widoczna dla robotów,
  dlatego każda odmiana ma własną statyczną stronę `wina/<slug>.html`.

### Panel redakcyjny poza aplikacją produkcyjną

- **Wybór**: `data/wina.json` edytuje się lokalnym panelem (`tools/panel/`), uruchamianym
  ręcznie i nasłuchującym wyłącznie na `127.0.0.1`. Nie jest częścią `wsgi.py` ani wdrożenia.
- **Dlaczego**: panel musi zapisywać plik, a produkcyjny serwer ma pozostać serwerem plików
  statycznych bez prawa zapisu. Rozdzielenie ich sprawia, że nawet błąd w konfiguracji
  wdrożenia nie wystawi zapisu do internetu.
- **Konsekwencja**: aktualizacja cennika to praca lokalna zakończona commitem i wdrożeniem —
  nie edycja „na żywo" na serwerze. Nie przenoś panelu do `wsgi.py`, nawet „tymczasowo".

### Front-end bez frameworka i bez modułów

- **Wybór**: jeden plik `main.js`, ES6, `defer`, funkcje `initX()` spinane w `DOMContentLoaded`.
- **Dlaczego**: strona ma pięć sekcji i jeden interaktywny element (sklep). Framework kosztowałby
  więcej niż cały obecny front-end.
- **Konsekwencja**: nie wprowadzamy `import`/`export`, bundlera ani biblioteki UI bez decyzji
  Właściciela. Nowa funkcjonalność = nowa funkcja `initX()`.

### Koszyk i formularz jako zaślepki

- **Wybór**: koszyk w pamięci, formularz i płatność kończą się `alert()`.
- **Dlaczego**: nie ma backendu, który przyjąłby zamówienie ani wiadomość.
- **Konsekwencja**: to nie są błędy do naprawienia „przy okazji". Uczynienie ich prawdziwymi
  to zadanie **L** — patrz `TODO.md` #7.
