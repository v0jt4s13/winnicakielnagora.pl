# Konwencje `main.js`

Jeden plik, ES6, bez modułów i bundlera, ładowany z `defer`. Brak `import`/`export` — wszystko
żyje w zasięgu pliku.

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
- **Ceny formatuj przez `formatPrice`**, nie ręcznym `toFixed(2) + " zł"`.

## Wyjątek: `alert()`

`initCart` (przycisk płatności) i `initContactForm` używają `alert()` jako świadomej zaślepki
demo. **Nie rozszerzaj tego wzorca** i pamiętaj, że `alert()` zawiesza automatyzację przeglądarki
— tych dwóch przycisków nie klikaj przez Chrome MCP.

## Why

Brak bundlera oznacza brak izolacji: jedyną strukturą pliku jest konwencja `initX()` + rejestracja
w jednym miejscu. Kiedy wszystko wisi na `DOMContentLoaded`, ta lista jest spisem treści front-endu.
