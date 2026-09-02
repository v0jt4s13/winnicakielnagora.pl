# Style: bundle Tailwinda vs. `custom.css`

W repo są dwa arkusze i mają różny status:

| Plik | Status | Co z nim wolno |
|---|---|---|
| `assets/css/style.css` | **artefakt tylko do odczytu** — zbudowany Tailwind, zminifikowany, jedna linia, bez źródeł (`package.json`, `tailwind.config`) | nic; nie edytować, nie formatować |
| `assets/css/custom.css` | ręcznie pisany CSS projektu | tu dopisujesz style |

## Reguła nadrzędna

**Klasa Tailwinda, której nie ma w bundlu, nie zadziała i nie da się jej dobudować.**
Zanim użyjesz nowej klasy utility, sprawdź, czy w bundlu istnieje:

```bash
grep -c 'line-clamp-2' assets/css/style.css
```

Jeśli nie ma — napisz regułę w `custom.css` albo użyj klasy, która w bundlu już jest.

## Reguły dla `custom.css`

- Kolory wyłącznie przez zmienne motywu: `hsl(var(--primary))`, nigdy wartość na sztywno
  (patrz `frontend/theming`).
- Nazwy klas komponentowe i kebab-case, tak jak istniejące: `.btn-primary`, `.hover-elevate`,
  `.cart-panel`, `.quantity-control`.
- Wcięcia 2 spacje, jedna deklaracja na linię.
- Style związane z jednym komponentem trzymaj razem, w kolejności: element → stan (`:hover`,
  `:active`) → warianty przeglądarkowe (`::-webkit-…`, `::-moz-…`).

## Why

Bundle jest artefaktem bez źródeł — to najpoważniejsze ograniczenie techniczne projektu.
Każda zmiana wyglądu musi się zmieścić albo w klasach, które już są, albo w `custom.css`.
