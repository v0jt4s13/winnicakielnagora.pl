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
3. **NEVER** zmieniaj ceny produktu tylko w jednym miejscu — komplet to `data-price`,
   `data-price-net`, widoczna cena, tekst `netto: … zł`, a przy promocji przekreślona cena
   sprzed rabatu i badge `-N%`. Patrz `.ai/standards/content/product-card.md`.
4. **NEVER** przeformatowuj `index.html` przy okazji innej zmiany — jeden plik jest jedyną kopią
   treści witryny, a duży diff jest nie do przejrzenia.
5. **NEVER** dodawaj zależności (Python, npm, CDN) bez zgody Właściciela — brak zależności jest
   tu decyzją, nie zaniedbaniem.

## Decision priorities

Gdy wartości są w konflikcie, rozstrzyga ta kolejność:

1. **Poprawność treści publicznej** — to strona firmowa; błędna cena, nieistniejąca odmiana albo
   martwy link są kosztowniejsze niż brzydki kod.
2. **Stabilność wyglądu we wszystkich trzech motywach** — złamany motyw widzi każdy odwiedzający.
3. **Czytelność diffu w `index.html`** — jedyna kontrola jakości, jaką ma tu recenzent.
4. **Brak nowych zależności** — projekt utrzymuje się sam dzięki temu, że nic nie wymaga budowania.
5. **Elegancja kodu** — ostatnia, nie pierwsza.

## Architectural boundaries

1. `assets/js/main.js` → **NIGDY** nie trzyma danych produktów. Źródłem prawdy są atrybuty
   `data-*` na kartach w `index.html`.
2. `assets/css/custom.css` → **NIGDY** nie duplikuje klas z bundla Tailwinda; dopisuje tylko to,
   czego w bundlu nie ma.
3. `wsgi.py` → **NIGDY** nie dostaje logiki biznesowej. To serwer plików statycznych; wszystko
   inne jest zadaniem rozmiaru **L** i wymaga decyzji Właściciela.
4. `attached_assets/` i `assets/` → jedyne miejsca na grafiki; ścieżki zawsze względne.

## Consistency rules

1. Dodajesz zmienną CSS → **ZAWSZE** do wszystkich trzech motywów w `themeStyles`.
2. Zmieniasz cenę produktu → **ZAWSZE** komplet sześciu miejsc na karcie (patrz BLOCK #3),
   przy zachowaniu `brutto = netto × 1.23`.
3. Dodajesz produkt → **ZAWSZE** unikalne `data-id`, `data-category` zgodne co do znaku
   z przyciskiem filtra, cena w zakresie 0–100 zł (inaczej wypadnie z filtra).
4. Dodajesz sekcję z `id` → **ZAWSZE** pozycja w nawigacji desktopowej i mobilnej
   (`data-scroll="id-sekcji"`), jeśli ma być osiągalna z menu.
5. Dodajesz zachowanie w JS → **ZAWSZE** jako `initX()` zarejestrowane w `DOMContentLoaded`.
6. Dodajesz ikonę → **ZAWSZE** jako `<symbol id="icon-…">` w ukrytym `<svg>` na początku `<body>`,
   używana przez `<use href="#icon-…">`.

## Allowed exceptions

1. **`alert()` w `initCart` i `initContactForm`** — świadome zaślepki demo, dopóki nie ma backendu.
   Nie rozszerzamy wzorca na nowy kod i pamiętamy, że blokują automatyzację przeglądarki.
2. **Koszyk w pamięci (`Map`), znikający po odświeżeniu** — świadomy stan demo, nie błąd.
3. **Bardzo długie linie atrybutów na kartach produktów** — celowe; nie łamiemy ich, bo diff
   stałby się nieczytelny.
4. **Zduplikowana cena netto w markupie** — dopóki `data-price-net` nie zostanie zlikwidowane
   albo zaczęte renderować z JS (patrz `TODO.md` #3).

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

### Dane produktów w HTML zamiast w bazie

- **Wybór**: każdy produkt to `<article class="product-card">` z atrybutami `data-*`.
- **Dlaczego**: sześć produktów i brak backendu — baza albo plik JSON dokładałyby warstwę,
  której nikt nie utrzymuje.
- **Konsekwencja**: cena jest zduplikowana w kilku miejscach jednej karty i nic tego nie waliduje.
  Pilnuje tego standard `content/product-card` i reguła BLOCK #3.

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
