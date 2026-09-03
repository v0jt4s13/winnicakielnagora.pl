# Motywy (`themeStyles`)

Witryna ma cztery motywy: `classic`, `modern`, `rustic`, `dark`. Każdy to obiekt
w `themeStyles` na górze `assets/js/main.js` z polem `colorScheme` oraz **tym samym kompletem
29 zmiennych CSS** (HSL bez `hsl()`). `dark` jest jedynym motywem ciemnym i jedynym, który
witryna potrafi włączyć sama — po zmroku, przez `initTimeTheme()`.

## Reguła nadrzędna

**Nowa zmienna CSS musi trafić do wszystkich czterech motywów jednocześnie.**

`setTheme` ustawia zmienne jako style inline na `document.documentElement` i **nigdy ich nie
czyści**:

```js
Object.entries(vars).forEach(([key, value]) => root.style.setProperty(key, value));
```

Zmienna obecna tylko w jednym motywie zostanie po przełączeniu z wartością z poprzedniego
motywu — bez błędu w konsoli, za to z rozjechanymi kolorami.

## Sprawdzenie parytetu

```bash
for t in classic modern rustic dark; do
  awk "/^  $t: \{/,/^  \},?\$/" assets/js/main.js | grep -c '"--'
done   # cztery razy ta sama liczba
```

## Reguły

- Kolory zapisuj jako `"H S% L%"` (bez `hsl()`) — tak konsumuje je bundle Tailwinda.
- Nie ustawiaj kolorów na sztywno w `custom.css`; używaj `hsl(var(--nazwa))`, inaczej element
  wypadnie z systemu motywów.
- Każdy motyw deklaruje `colorScheme` (`light` albo `dark`), a `setTheme` przekazuje tę
  wartość do `document.documentElement.style.colorScheme`.
- Wybrany motyw ląduje w `localStorage["winery-style"]`; domyślny (brak wpisu) to `classic`.
- Automatyczne, chwilowe przełączenie wyglądu wywołuje `setTheme(style, false)`, żeby nie
  nadpisać ręcznie zapisanej preferencji. Nocna pora jest takim przełączeniem na `dark`;
  po wyjściu z niej wraca `preferredTheme()`.
- Motyw, który witryna włącza sama, musi być **osobną pozycją**, a nie przemalowaniem
  istniejącej. `modern` był przez chwilę ciemny i rozjeżdżał się z własnym opisem w menu
  („Minimalistyczny z czystymi liniami"); dlatego ciemna paleta ma dziś własny klucz `dark`.
- Reguła czasowa motywu należy do osobnego `initTimeTheme()`, niezależnego od
  `initHeroImage()`. Podstrony odmian ładują `main.js`, ale nie mają `#hero-image`, więc
  inicjalizator obrazu nie może odpowiadać za wygląd całej witryny.
- Każda zmiana kolorów lub CSS wymaga obejrzenia strony we **wszystkich czterech** motywach.
- Każdy motyw z `themeStyles` ma mieć pozycję w menu stylu (`.style-option[data-style]`
  w `index.html`) — inaczej da się go włączyć tylko automatycznie albo przez `localStorage`.

## Why

Motywy to jedyny mechanizm „konfiguracji" wyglądu w tym projekcie i jedyne miejsce, gdzie brak
symetrii psuje stronę po cichu — inline style przeżywają przełączenie motywu.
