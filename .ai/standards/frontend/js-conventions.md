# Konwencje JS

Dwa pliki, ES6, bez modułów i bundlera, ładowane z `defer`. Brak `import`/`export` — wszystko
żyje w zasięgu pliku albo w jednym globalnym obiekcie.

| Plik | Rola | Uruchamia coś przy wczytaniu? |
|---|---|---|
| `assets/js/produkty.js` | biblioteka: wyliczenia cen i render karty produktu (obiekt `Produkty`) | **nie** — zero zdarzeń, zero DOM |
| `assets/js/main.js` | zachowanie strony: `initX()` spięte w `DOMContentLoaded` | tak |

Kolejność w HTML: `produkty.js` **przed** `main.js`. Powód rozdzielenia: panel redakcyjny
używa `Produkty.renderProductCard()` do podglądu i nie może wczytać `main.js`, bo ten odpaliłby
całą inicjalizację strony. Szczegóły: `.ai/GUARDRAILS.md` → „Front-end bez frameworka i bez
modułów, w dwóch plikach".

## Wzorzec: jedna funkcja `initX()` na obszar

```js
function initFilters() {
  const promoOnly = qs("#promo-only");
  promoOnly?.addEventListener("change", applyFilters);
}

document.addEventListener("DOMContentLoaded", () => {
  initStyleSwitcher();
  initNavigation();
  initFilters();
  initCart();
  initContactForm();
});
```

- **Nowe zachowanie = nowa funkcja `initX()`** + wpis w `DOMContentLoaded`. Nie dopisuj
  nasłuchiwaczy do istniejących `init*`, jeśli dotyczą innego obszaru strony.
- **Zawsze `qs` / `qsa`**, nie `document.querySelector` wprost:
  ```js
  const qs  = (sel) => document.querySelector(sel);
  const qsa = (sel) => Array.from(document.querySelectorAll(sel));
  ```
- **Optional chaining na każdym elemencie DOM** (`el?.addEventListener`, `qs("#x")?.classList`).
  Strona ma jeden HTML, ale funkcje muszą przeżyć usunięcie sekcji z markupu.
- **Stan tylko w pamięci**: koszyk to `const cart = new Map()`. Do `localStorage` idzie wyłącznie
  wybrany motyw (klucz `winery-style`). Nie dokładaj tam nic bez ustalenia z Właścicielem.
- **Dane czytaj z `dataset`**, nie z tekstu w DOM — źródłem prawdy o produkcie są atrybuty
  `data-*` na karcie (patrz `content/product-card`).
- **Ceny formatuj przez `Produkty.formatujCene()`** — jedyna funkcja formatująca kwoty
  w projekcie, używana zarówno przez sklep, koszyk, jak i panel. Nie pisz `toFixed(2) + " zł"`
  i nie dokładaj drugiej takiej funkcji w `main.js`.

## Wyjątek: `alert()`

`initCart` (przycisk płatności) i `initContactForm` używają `alert()` jako świadomej zaślepki
demo. **Nie rozszerzaj tego wzorca** i pamiętaj, że `alert()` zawiesza automatyzację przeglądarki
— tych dwóch przycisków nie klikaj przez Chrome MCP.

## Why

Brak bundlera oznacza brak izolacji: jedyną strukturą pliku jest konwencja `initX()` + rejestracja
w jednym miejscu. Kiedy wszystko wisi na `DOMContentLoaded`, ta lista jest spisem treści front-endu.
