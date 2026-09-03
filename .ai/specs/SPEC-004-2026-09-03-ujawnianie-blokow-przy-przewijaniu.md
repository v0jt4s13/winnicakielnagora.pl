# Ujawnianie bloków przy przewijaniu

## Overview

Strona główna ma subtelnie ujawniać kolejne główne bloki, gdy użytkownik przewija dokument
i odkrywa nowe treści. Efekt jest progresywnym ulepszeniem: treść pozostaje w HTML, zachowuje
indeksowalność i dostępność, a bez JavaScript lub bez wymaganych API jest od razu widoczna.

Animacja nie obejmuje hero, stałego nagłówka, panelu koszyka ani strony 404. Te elementy
muszą być dostępne natychmiast. Każdy obserwowany blok animuje się tylko raz podczas wizyty.

## User Stories

### 1. Zwiedzający odkrywa kolejne sekcje strony

**Persona:** osoba poznająca winnicę na laptopie lub telefonie, przewijająca stronę od hero
do informacji, odmian, sklepu, degustacji i kontaktu.

1. Hero i nawigacja są widoczne od razu, bez efektu wejścia.

   ```text
   ┌──────────────────────────────────────┐
   │ hero + nawigacja     widoczne od razu│
   └──────────────────────────────────────┘
                    ↓ przewijanie
   ┌──────────────────────────────────────┐
   │ nowy blok      ↑ 24 px + fade-in     │
   └──────────────────────────────────────┘
   ```

2. Gdy główny blok wejdzie w dolną część viewportu, płynnie przesuwa się w górę o niewielką
   wartość i zwiększa krycie do pełnego.

3. Po ujawnieniu blok pozostaje widoczny. Przewinięcie w górę nie odtwarza animacji.

   **Za kulisami:** `initScrollReveal()` tworzy jeden `IntersectionObserver`, dodaje klasę
   `.is-visible` i natychmiast przestaje obserwować ujawniony element.

   > **Zmiana vs. stan obecny:** obecnie wszystkie sekcje są statyczne. Po zmianie tylko
   > oznaczone, główne bloki dostają krótki efekt wejścia podczas pierwszego odkrycia.

### 2. Użytkownik ograniczający ruch lub przeglądarka bez obsługi API

**Persona:** osoba z włączonym `prefers-reduced-motion: reduce` albo korzystająca ze starszej
przeglądarki. Jej celem jest natychmiastowy dostęp do całej treści bez ruchu i bez znikających
bloków.

1. Skrypt wykrywa preferencję ograniczonego ruchu lub brak `IntersectionObserver`.

2. Wszystkie elementy `[data-reveal]` otrzymują od razu stan `.is-visible`, także gdy
   preferencja zostanie włączona już po otwarciu strony. Obserwator zostaje wtedy odłączony.

   ```text
   prefers-reduced-motion / brak API
                    │
                    ▼
   [data-reveal].is-visible → brak transformacji i przejścia
   ```

3. Nawigacja, filtry, koszyk i formularz działają jak przed zmianą.

   **Za kulisami:** media query wymusza `opacity: 1`, `transform: none`, brak `transition`
   i brak `will-change`. Inicjalizator nasłuchuje zmiany `MediaQueryList`; po włączeniu
   ograniczonego ruchu ujawnia wszystkie targety i wyłącza obserwator. Brak JavaScript również
   nie ukrywa treści, bo klasa startowa jest dodawana wyłącznie przez krótki skrypt w `<head>`.

   > **Zmiana vs. stan obecny:** wizualnie brak zmiany dla osoby ograniczającej animacje;
   > dochodzi wyłącznie gwarancja, że mechanizm ujawniania nigdy nie blokuje treści.

## Porównanie wariantów

| Warunek | Zachowanie |
|---|---|
| Standardowa przeglądarka | Jednorazowe fade-in i przesunięcie `24px → 0` |
| `prefers-reduced-motion: reduce` | Treść natychmiast widoczna, bez przejścia |
| Brak `IntersectionObserver` | Treść natychmiast widoczna |
| Brak JavaScript | Treść widoczna dzięki brakowi klas sterujących |
| Powrót do już odkrytego bloku | Bez ponownej animacji |

## Architecture

### HTML

`index.html` otrzymuje atrybut `data-reveal` na dokładnie 18 istniejących blokach:

- `#o-nas > .max-w-7xl > .grid` — 1,
- `#nasze-wina > .max-w-7xl > .text-center` — 1,
- `#nasze-wina > .max-w-7xl > .space-y-12 > article` — 7,
- `#sklep > .max-w-7xl > .text-center` — 1,
- `#sklep > .max-w-7xl > .grid > aside` — 1,
- `#sklep > .max-w-7xl > .grid > .lg\:col-span-3` — 1,
- `#wydarzenia > .max-w-7xl > .text-center` — 1,
- `#wydarzenia > .max-w-7xl > .rounded-md` — 1,
- `#kontakt > .max-w-7xl > .text-center` — 1,
- `#kontakt > .max-w-7xl > .grid > .space-y-8` — 1,
- `#kontakt > .max-w-7xl > .grid > .rounded-md.bg-card` — 1,
- `footer > .max-w-7xl > .grid` — 1.

Żaden `[data-reveal]` nie może być potomkiem innego `[data-reveal]`. Zapobiega to podwójnemu
ukryciu i niespójnym animacjom rodzica oraz dziecka.

Treść, kolejność DOM, nagłówki, linki oraz atrybuty SEO nie zmieniają się. Hero, nagłówek,
koszyk i `404.html` nie otrzymują znacznika.

### CSS

`assets/css/custom.css` definiuje stan w obecności `.reveal-pending` lub `.reveal-ready`
na elemencie `<html>`:

- początek: `opacity: 0`, `transform: translateY(24px)`,
- koniec `.is-visible`: `opacity: 1`, `transform: translateY(0)`,
- przejście: `600ms cubic-bezier(0.22, 1, 0.36, 1)`,
- `will-change` jest usuwane w stanie końcowym,
- `prefers-reduced-motion: reduce` wymusza `opacity: 1`, `transform: none`,
  `transition: none` i `will-change: auto` niezależnie od klas dokumentu.

W `<head>` przed arkuszami znajduje się minimalny skrypt startowy. Dodaje `.reveal-pending`
przed pierwszym wyliczeniem stylów, dzięki czemu nie ma sekwencji „widoczne → ukryte”. Ten sam
skrypt rejestruje jednorazowy fallback `DOMContentLoaded`: jeśli główny inicjalizator nie
zamieni `.reveal-pending` na `.reveal-ready`, usuwa klasę w następnym `requestAnimationFrame`
i ujawnia całą treść. Przy wyłączonym JavaScript skrypt nie działa, więc treść również pozostaje
widoczna.

### JavaScript

Nowa funkcja `initScrollReveal()` w `assets/js/main.js`:

1. pobiera wszystkie `[data-reveal]`,
2. jeśli lista jest pusta — usuwa `.reveal-pending` i kończy działanie,
3. dla ograniczonego ruchu lub braku `IntersectionObserver` ujawnia wszystko natychmiast
   i usuwa klasy sterujące,
4. jeśli adres zawiera kotwicę, ujawnia przed uruchomieniem obserwatora każdy blok zawierający
   wskazany element oraz każdy blok wewnątrz wskazanej sekcji,
5. w `try` tworzy jeden obserwator z `rootMargin: "0px 0px -10% 0px"` i `threshold: 0.08`,
   zaczyna obserwować targety, następnie dodaje `.reveal-ready` i usuwa `.reveal-pending`,
6. przy pierwszym przecięciu dodaje `.is-visible` i wykonuje `unobserve(element)`,
7. nasłuchuje `prefers-reduced-motion`; po zmianie na `reduce` ujawnia wszystko i wywołuje
   `disconnect()`,
8. `catch` zawsze dodaje `.is-visible` do wszystkich targetów oraz usuwa `.reveal-pending`
   i `.reveal-ready`, więc wyjątek inicjalizacji nie może pozostawić ukrytej treści.

Inicjalizator zostaje wywołany w istniejącym `DOMContentLoaded`. Nie dodajemy bibliotek,
timerów ani globalnego stanu.

## Data Models

Brak nowych danych oraz zmian w `data/wina.json`.

## API Contracts

Brak nowych endpointów, żądań sieciowych i integracji zewnętrznych.

## UI/UX

- Ruch jest subtelny i nie opóźnia interakcji z elementem po jego wejściu w viewport.
- Elementy nie przesuwają układu, ponieważ animowany jest wyłącznie `transform` i `opacity`.
- Treść zachowuje kontrast oraz wygląd w `classic`, `modern` i `rustic`.
- Telefon i desktop używają tego samego mechanizmu; niewielkie przesunięcie nie powoduje
  przepełnienia poziomego.
- Dynamiczna lista produktów ujawnia się jako jeden blok, a nie seria opóźniających się kart.
- Obserwowany jest istniejący wrapper `.lg\:col-span-3`, nie pusty `#lista-produktow`.
  Wrapper od początku ma wysokość dzięki regułom `#lista-produktow:empty`, więc kolejność
  pobrania cennika nie wpływa na obserwator. `initScrollReveal()` może zostać wywołane przed
  asynchronicznym `wczytajCennik()`.

## Configuration

Brak konfiguracji środowiskowej. Parametry ruchu są częścią lokalnych reguł CSS i konfiguracji
jednego obserwatora.

## Kryteria akceptacji

- Oznaczone bloki płynnie pojawiają się podczas pierwszego wejścia w viewport.
- Ujawniony blok nie znika i nie animuje się ponownie.
- Element widoczny przy pierwszym renderze zostaje ujawniony przez pierwszy callback obserwatora.
- Wejście bezpośrednio przez kotwicę, np. `/#kontakt`, ujawnia docelowe bloki bez trwałego
  `opacity: 0`.
- Hero, nagłówek, koszyk oraz 404 są widoczne natychmiast.
- Bez JavaScript i bez `IntersectionObserver` komplet treści pozostaje widoczny.
- Awaria inicjalizatora po dodaniu klasy startowej przywraca widoczność wszystkich bloków.
- `prefers-reduced-motion: reduce`, również włączone w trakcie sesji, wyłącza animację
  i ujawnia wszystkie bloki.
- Brak skoków layoutu i przepełnienia poziomego na telefonie oraz desktopie.
- Efekt działa w `classic`, `modern` i `rustic`.
- Filtry, koszyk, formularz i nawigacja zachowują dotychczasowe działanie.
- Konsola przeglądarki nie zgłasza błędów.

## Implementation Checklist

- [x] Wstrzyknąć uzgodnione standardy.
- [x] Dodać bezpieczny skrypt `.reveal-pending` w `<head>` pliku `index.html`.
- [x] Oznaczyć dokładnie 18 głównych bloków w `index.html` przez `data-reveal`.
- [x] Dodać stany animacji i obsługę ograniczonego ruchu w `assets/css/custom.css`.
- [x] Dodać `initScrollReveal()` i rejestrację w `assets/js/main.js`.
- [x] Zweryfikować przewijanie, fallbacki, trzy motywy i widoki responsywne.
- [x] Uruchomić końcową weryfikację standardów.
- [x] Selektywnie zacommitować ukończone zmiany bez narzędzi testowych `?hero=`.

## Implementation Review

- `index.html` zawiera dokładnie 18 niezagnieżdżonych elementów `[data-reveal]`.
- Standardowy przebieg sprawdzono w Chrome: blok startuje z `opacity: 0` i przesunięciem
  `24px`, jest widoczny w trakcie przejścia, a po 600 ms pozostaje w stanie `.is-visible`.
- Bezpośrednie wejście przez `/#kontakt` natychmiast ujawnia wszystkie trzy bloki sekcji.
- `prefers-reduced-motion: reduce`, zarówno przy starcie, jak i włączone w trakcie sesji,
  ujawnia wszystkie bloki z `transition-duration: 0s`.
- Brak `IntersectionObserver` oraz kontrolowany wyjątek jego konstruktora kończą się pełną
  widocznością treści i usunięciem klas sterujących.
- Widok 390 × 844 px nie ma przepełnienia poziomego; efekt sprawdzono także na desktopie
  1440 × 900 px oraz w `classic`, `modern` i `rustic`.
- Strona 404 nie ma elementów `[data-reveal]`, nie otrzymuje `.reveal-pending` i nadal zwraca
  HTTP 404.
- `node --check`, testy `tools/test-produkty.js` i `git diff --check` zakończyły się poprawnie.
- Kod jest zgodny z `content/html-editing`, `frontend/js-conventions` i `frontend/styling`.

## Changelog

### 2026-09-03

- Pierwsza wersja specyfikacji efektu ujawniania bloków podczas przewijania.
- Wdrożono jednorazowe ujawnianie 18 bloków, fallbacki oraz obsługę ograniczonego ruchu.
