# Design QA — strona 404 na niskich ekranach

## Materiał porównawczy

- Źródło prawdy: dwa zrzuty Chrome załączone przez użytkownika w bieżącej rozmowie,
  przedstawiające stronę 404 przy wymiarach CSS 1150 × 531 px i 1366 × 638 px.
- Znormalizowane odtworzenie stanu źródłowego:
  `/tmp/winnica-404-height-before-1150x531.png` i
  `/tmp/winnica-404-height-before-1366x638.png`.
- Implementacja:
  `/tmp/winnica-404-height-after-1150x531.png` i
  `/tmp/winnica-404-height-after-1366x638.png`.
- Porównania w jednym obrazie, stan przed po lewej i po zmianie po prawej:
  `/tmp/winnica-404-height-compare-1150x531.png` i
  `/tmp/winnica-404-height-compare-1366x638.png`.
- Viewporty: 1150 × 531 px i 1366 × 638 px; `deviceScaleFactor: 1`; bez skalowania
  gęstości obrazu. Stan: nieistniejąca ścieżka `/sd`, wariant `noc`, motyw `modern`.

## Findings

Brak pozostałych problemów P0, P1 lub P2.

### Historia porównania

- [P1] Dolne elementy strony były niedostępne na niskim ekranie.
  - Lokalizacja: `.error-page`, `.error-page__actions`, `.error-page__shortcuts`.
  - Dowód przed zmianą: przy 1150 × 531 px oba CTA zaczynały się poza dolną krawędzią;
    przy 1366 × 638 px niewidoczne były skróty i lokalizacja.
  - Poprawka: breakpoint `(min-width: 641px) and (max-height: 899px)` zmniejsza wyłącznie
    pionowe odstępy, typografię nagłówkową i wysokość CTA.
  - Dowód po zmianie: przy 1150 × 531 px lokalizacja kończy się na 453.11 px, a przy
    1366 × 638 px na 493.84 px. `scrollHeight` jest równy wysokości viewportu w obu stanach.

## Pełny widok

Kompozycja zachowuje lewą oś, hierarchię i nocny kadr. Po zmianie pełna ścieżka treści —
kod błędu, tytuł, opis, CTA, trzy skróty i lokalizacja — jest widoczna jednocześnie.

Osobny wycinek nie był potrzebny: problem obejmował pionową kompozycję całego ekranu,
a czytelność najniższych elementów potwierdzono zarówno wizualnie, jak i pomiarem DOM.

## Wymagane powierzchnie jakości

- Typografia: zachowano Playfair Display i Lato, wagi oraz hierarchię; zmniejszone rozmiary
  nadal są czytelne i nie powodują niekontrolowanego zawijania.
- Rytm i layout: wszystkie elementy mieszczą się bez przewijania oraz bez przepełnienia
  poziomego w obu viewportach.
- Kolory i tokeny: bez zmian; sprawdzono `classic`, `modern` i `rustic`.
- Jakość obrazu: zachowano oryginalne `noc.png`, `object-fit: cover` i ostrość kadru.
- Treść: komplet tekstów, oba CTA, trzy skróty i lokalizacja pozostają obecne.

## Interakcje i konsola

- Linki zachowują istniejące cele i dostępne stany focus; poprawka nie zmienia zachowania.
- Sprawdzono wariant mobilny 390 × 844 px oraz wysoki desktop 1440 × 1000 px — istniejące
  breakpointy pozostają bez zmian.
- Podczas pomiarów w Chrome nie wystąpiły wyjątki JavaScript.

## Implementation Checklist

- [x] Breakpoint wysokościowy działa wyłącznie na desktopie poniżej 900 px.
- [x] Pełna zawartość mieści się przy 1150 × 531 px i 1366 × 638 px.
- [x] Brak regresji motywów, szerokiego desktopu i widoku mobilnego.

final result: passed
