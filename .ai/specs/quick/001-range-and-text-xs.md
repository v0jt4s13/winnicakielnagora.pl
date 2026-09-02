# Suwak cen i skala `.text-xs`

## Zakres

- Osadzić oba uchwyty suwaka cen na pionowej osi `#range-highlight`.
- Ustawić wypełnienie uchwytów na ten sam kolor motywu co ramka i aktywna linia.
- Nadpisać `.text-xs` wartościami `font-size: 1.15rem` i `line-height: 1.6rem`.
- Nie edytować prebudowanego `assets/css/style.css` ani logiki zakresu cen.

## Implementacja

- [x] Standardy `frontend/styling` i `frontend/theming` zastosowane.
- [x] Style poprawione w `assets/css/custom.css`.
- [x] Wygląd sprawdzony w motywach `classic`, `modern` i `rustic`.

## Weryfikacja

- `#range-highlight` i oba pola `range` mają wspólny środek pionowy (`458.75 px` przy
  viewportcie 390 × 844 px).
- `.text-xs` oblicza się w Chrome do `18.4 px / 25.6 px`, czyli dokładnie
  `1.15rem / 1.6rem` przy bazowym `16 px`.
- Brak przewijania poziomego w sprawdzonej sekcji sklepu (`scrollWidth = 390 px`).
- Motywy `classic`, `modern` i `rustic` zachowują właściwy kolor linii i uchwytów.

## Powód

W dotychczasowym układzie `#range-highlight` był przyklejony do górnej krawędzi przez
`inset: 0`, a suwaki nie miały jawnej wspólnej osi pionowej. Powodowało to widoczne
rozminięcie linii i uchwytów.
