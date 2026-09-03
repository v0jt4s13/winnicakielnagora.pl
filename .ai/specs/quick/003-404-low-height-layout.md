# Strona 404 na niskich ekranach

## Zakres

- Pokazać komplet treści strony 404 przy desktopowej szerokości i wysokości poniżej 900 px.
- Zachować nagłówek, komunikat, oba CTA, trzy skróty oraz lokalizację bez przewijania dla
  referencyjnych viewportów 1150 × 531 px i 1366 × 638 px.
- Nie zmieniać układu mobilnego ani wersji dla ekranów o wysokości co najmniej 900 px.

## Implementacja

- [x] Dodać breakpoint wysokościowy `(min-width: 641px) and (max-height: 899px)`.
- [x] Zmniejszyć wyłącznie pionowe odstępy, rozmiar nagłówka `404` i tytułu oraz wysokość CTA.
- [x] Sprawdzić oba referencyjne viewporty, wszystkie trzy motywy i brak przepełnienia.

## Weryfikacja

- Przy 1150 × 531 px ostatni element kończy się na `453.11 px`, a `scrollHeight` strony
  jest równy wysokości viewportu (`531 px`).
- Przy 1366 × 638 px ostatni element kończy się na `493.84 px`, a `scrollHeight` strony
  jest równy wysokości viewportu (`638 px`).
- Wyniki są identyczne dla `classic`, `modern` i `rustic`; brak przepełnienia poziomego.
- Konsola Chrome nie zgłasza wyjątków JavaScript.

## Powód

Dotychczas kontener centrował wysoką kolumnę treści i miał `overflow: hidden`. Na niskich
ekranach dolne CTA, skróty oraz lokalizacja wypadały poza viewport, mimo dostępnej szerokości.
