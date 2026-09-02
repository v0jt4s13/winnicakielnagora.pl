# Edycja `index.html`

`index.html` to jedyna kopia treści witryny — ~790 linii, wszystkie sekcje w jednym pliku.
**Zmieniaj wyłącznie fragment, którego dotyczy zadanie.**

## Reguły

- **Nie przeformatowuj przy okazji.** Żadnego porządkowania wcięć, przenoszenia atrybutów ani
  „poprawiania" sąsiedniego markupu — diff musi pokazywać samą zmianę merytoryczną.
- **Wcięcia: 2 spacje**, tak jak w sąsiednim kodzie. Atrybuty zostają w jednej linii, nawet
  długiej (karty produktów mają po kilkanaście atrybutów w jednym wierszu — to celowe).
- **Nowa sekcja** dostaje `id` w kebab-case po polsku (`o-nas`, `nasze-wina`, `wydarzenia`)
  i klasę `py-20`; jeśli ma się pojawić w nawigacji, dodaj też pozycję menu w nagłówku
  (desktop i mobile) — nawigacja działa przez `data-scroll="id-sekcji"`.
- **Ikony to `<symbol>`**, nie inline SVG. Wszystkie leżą w ukrytym `<svg>` na początku `<body>`.
  Użycie: `<svg class="w-4 h-4"><use href="#icon-cart"></use></svg>`. Nowa ikona = nowy
  `<symbol id="icon-…">` w tym bloku, nie wklejony `<path>` w treści.
- **Obrazy: ścieżki względne** i zawsze `alt` w języku polskim (`alt=""` dla obrazu
  czysto dekoracyjnego). Prawdziwe fotografie trzymaj w `attached_assets/photos/`, grafiki
  generowane w `attached_assets/generated_images/`, a zasoby interfejsu w `assets/`.
- **Treść jest po polsku i wpisana wprost** — nie ma i18n ani kluczy tłumaczeń. Nie wprowadzaj
  ich „na zapas".

## Kotwice zamiast numerów linii

Numery linii przestają być prawdziwe po pierwszej edycji treści. Szukaj po `id` i klasach:

```bash
grep -n 'id="sklep"' index.html
grep -n 'class="product-card' index.html
grep -n '<symbol' index.html
```

## Why

Jeden wielki plik znosi tylko punktowe edycje. Przy każdej zmianie treści numeracja linii się
przesuwa, więc dokumentacja i komunikacja muszą operować kotwicami, a diff musi zostać mały,
żeby dało się go przejrzeć.
