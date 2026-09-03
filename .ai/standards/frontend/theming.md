# Motywy (`themeStyles`)

Witryna ma trzy motywy: `classic`, `modern`, `rustic`. Każdy to obiekt w `themeStyles`
na górze `assets/js/main.js` z polem `colorScheme` oraz **tym samym kompletem 29 zmiennych
CSS** (HSL bez `hsl()`).

## Reguła nadrzędna

**Nowa zmienna CSS musi trafić do wszystkich trzech motywów jednocześnie.**

`setTheme` ustawia zmienne jako style inline na `document.documentElement` i **nigdy ich nie
czyści**:

```js
Object.entries(vars).forEach(([key, value]) => root.style.setProperty(key, value));
```

Zmienna obecna tylko w jednym motywie zostanie po przełączeniu z wartością z poprzedniego
motywu — bez błędu w konsoli, za to z rozjechanymi kolorami.

## Sprawdzenie parytetu

```bash
for t in classic modern rustic; do
  awk "/^  $t: \{/,/^  \},?\$/" assets/js/main.js | grep -c '"--'
done   # trzy razy ta sama liczba
```

## Reguły

- Kolory zapisuj jako `"H S% L%"` (bez `hsl()`) — tak konsumuje je bundle Tailwinda.
- Nie ustawiaj kolorów na sztywno w `custom.css`; używaj `hsl(var(--nazwa))`, inaczej element
  wypadnie z systemu motywów.
- Każdy motyw deklaruje `colorScheme` (`light` albo `dark`), a `setTheme` przekazuje tę
  wartość do `document.documentElement.style.colorScheme`.
- Wybrany motyw ląduje w `localStorage["winery-style"]`; domyślny (brak wpisu) to `classic`.
- Automatyczne, chwilowe przełączenie wyglądu wywołuje `setTheme(style, false)`, żeby nie
  nadpisać ręcznie zapisanej preferencji. Nocny kadr hero jest takim przełączeniem na
  `modern`; po wyjściu z okresu nocnego wraca `preferredTheme()`.
- Każda zmiana kolorów lub CSS wymaga obejrzenia strony we **wszystkich trzech** motywach.

## Why

Motywy to jedyny mechanizm „konfiguracji" wyglądu w tym projekcie i jedyne miejsce, gdzie brak
symetrii psuje stronę po cichu — inline style przeżywają przełączenie motywu.
