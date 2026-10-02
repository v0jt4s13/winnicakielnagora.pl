# Menu i stopka — jedna zmiana, wszystkie strony

Menu (nagłówek) i stopka są **skopiowane do każdej strony witryny**, nie ma szablonu ani include'a.
Zmiana etykiety, linku lub kolejności w menu albo w stopce = ta sama zmiana w **każdym** pliku z listy.

## Gdzie to jest (12 plików)

| Plik | Prefiks linków | Menu: desktop + mobile | Stopka |
|---|---|---|---|
| `index.html` | `#sekcja` + `data-scroll` (poza `sklep.html`, `odmiany-winogron.html`) | tak | tak |
| `sklep.html`, `noclegi.html`, `odmiany-winogron.html` | `./index.html#sekcja`, `./sklep.html` | tak | tak |
| `wina/*.html` (8 plików) | `../index.html#sekcja`, `../sklep.html` | tak | skrócona, bez „Szybkich linków" |

Nie dotyczy: `404.html` (własny blok skrótów), `plan-startu.html` (strona wewnętrzna).

## Obowiązujące pozycje (w tej kolejności, w menu i w stopce)

| Etykieta | Cel |
|---|---|
| O Nas | `index.html#o-nas` |
| Nasze wina | `sklep.html` |
| Wydarzenia | `index.html#wydarzenia` |
| Noclegi | `index.html#noclegi` — **tymczasowo** (2026-10-02), docelowo `noclegi.html`; strona istnieje, ale menu jej nie linkuje |
| Odmiany winogron | `odmiany-winogron.html` |
| Kontakt | `index.html#kontakt` |

## Reguły

- Menu ma **dwie kopie w każdym pliku**: `hidden md:flex` (desktop) i `#mobile-menu`. Zmień obie.
- Stopka z „Szybkimi linkami" (`index.html`, `sklep.html`, `noclegi.html`, `odmiany-winogron.html`) ma własną, trzecią listę — też ją zmień.
- Na stronie, którą pozycja wskazuje, daj `aria-current="page"` (robią tak `sklep.html` i `noclegi.html`).
- Na podstronach nie dawaj `data-scroll` do linków prowadzących na inną stronę.
- Po zmianie sprawdź wszystkie pliki jednym poleceniem:

```bash
grep -ho '<a href="[^"]*"[^>]*>[^<]*<' index.html sklep.html noclegi.html odmiany-winogron.html wina/*.html \
  | sed 's/class="[^"]*"//' | sort | uniq -c
```

Liczby przy tych samych etykietach muszą się zgadzać (po 2 w menu każdej strony, po 1 w stopce).

## Dlaczego

Brak szablonu to świadoma cena „zero kroku budowania". Skutek uboczny: pominięty plik oznacza menu,
które na jednej stronie mówi co innego niż na pozostałych (tak już raz było: „Cennik win" vs „Nasze wina").
