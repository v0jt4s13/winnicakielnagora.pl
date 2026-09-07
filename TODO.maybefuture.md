# TODO — może w przyszłości

Sprawy związane ze sprzedażą online albo świadomie zawieszone. Nie są w `TODO.md`, bo
nie planujemy ich teraz — wróci tu Właściciel, gdy zdecyduje, że sklep rusza, albo gdy
odblokuje się dana infrastruktura. Zamknięte pozycje są w `TODONE.md`.

Ostatnia aktualizacja: **2026-09-07**.

## Sklep i koszyk

### 7. Koszyk i formularz są zaślepkami

- Koszyk to `Map` w pamięci — znika po odświeżeniu strony.
- Formularz kontaktowy robi `preventDefault()` + `alert()`, nie wysyła nic; przycisk płatności
  też kończy się `alert()`.
- **Pytanie**: czy i kiedy dokładamy backend (wysyłka maila, trwały koszyk, płatności)? To
  zadanie rozmiaru **L** — dokłada projektowi zależność, której świadomie nie ma
  (`.ai/GUARDRAILS.md` → Architectural decisions).
- **Uwaga dla agentów**: `alert()` zawiesza automatyzację przeglądarki — tych przycisków nie
  klikaj przez Chrome MCP.

### 9 (reszta). Dane do faktury

Adres, telefon i e-mail są na stronie; mapa i `Organization` w JSON-LD zrobione
(`TODONE.md` #9). Zostaje tylko: **NIP i dane do faktury** — potrzebne dopiero, jeśli
rusza sprzedaż.

### 34. Cennik z produkcji nie wraca do repozytorium — niski priorytet

Panel działa i Właściciel zapisuje zmiany wyłącznie na serwerze (2026-09-02:
`seyval-blanc-2022` → `seyval-blanc-2023`). Wersja startowa w `data/wina.json` rozjeżdża się
z produkcją — tak jak przewiduje wariant A z #26 (`TODONE.md`).

Zgranie produkcji do repozytorium:

```bash
scp ops02:/opt/apps/app_winnicakielnagora.pl/dane/wina.json data/wina.json
```

Właściciel uznał to za mało istotne (2026-09-03). Notatka na przyszłość: jedyną kopią
produkcyjnego cennika jest `wina.json.bak` obok oryginału, więc skasowanie katalogu `dane/`
zabiera i cennik, i kopię. Zadanie w `production_tasks.json` kopiujące plik raz na dobę
rozwiązałoby sprawę.

### 38. Sklep ukryty, nie usunięty — jak przywrócić sprzedaż online

Sprzedaż online wyłączona na start (`TODONE.md` #23). Kod sklepu, koszyka i `data/wina.json`
**zostają nietknięte**. Wyłącza je:

- `const SKLEP_WLACZONY = false;` w `assets/js/main.js` (osłania blok sklepowy w `DOMContentLoaded`),
- `hidden` na `<section id="sklep">`, `#cart-button`, `#cart-overlay`, `#cart-panel` w `index.html`,
- brak pozycji „Sklep" w nawigacji (desktop, mobile, stopka) i w nagłówkach `wina/*.html`,
- blok `#oferta-odmiany` na podstronach odmian kieruje do `#kontakt` zamiast `#sklep`.

Przywrócenie = odwrócenie powyższego. **Nie usuwać kodu koszyka bez decyzji Właściciela** —
patrz `.ai/GUARDRAILS.md` → „Architectural boundaries".

## Zawieszone / czeka na decyzję infrastrukturalną

### 8. `dist/public` — build, którego nie ma

- **Gdzie**: `wsgi.py` → `STATIC_CANDIDATES`
- **Stan**: kod preferuje `dist/public`, ale wdrożenie nie ma kroku budowania, więc na produkcji
  serwowany jest katalog repo. Gałąź `dist/public` jest martwa.
- **Pytanie**: dodajemy build, czy usuwamy tę gałąź z `wsgi.py`?
