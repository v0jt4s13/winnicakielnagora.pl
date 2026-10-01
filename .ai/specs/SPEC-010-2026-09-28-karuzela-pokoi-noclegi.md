# SPEC-010 — Karuzela zdjęć pokoi w sekcji `#noclegi`

Rozmiar: **M** (nowe zachowanie w `main.js` + publiczny endpoint listujący katalog).
Zależy od SPEC-009 (wgrywanie, galeria panelu, dowiązanie `uploads`).

## Overview

W karcie rezerwacji (`#noclegi`), pod nagłówkiem „Zarezerwuj nocleg w winnicy”, a nad formularzem
Booking.com pojawia się karuzela miniatur pokoi. Kliknięcie miniatury otwiera podgląd
pełnego zdjęcia (GLightbox, już w repo). Zdjęcia pochodzą z katalogu `attached_assets/pokoje/`:

- miniatura w karuzeli: `{nazwa}-thumb.{ext}` (wariant 300 px z galerii panelu),
- podgląd: `{nazwa}.{ext}` — ten sam rdzeń nazwy, dowolne z rozszerzeń obrazów.

Pokazujemy wyłącznie **pary** (miniatura + pełne). Kolejność: alfabetycznie po nazwie — Właściciel
steruje nią nazwami (`01-salon`, `02-lazienka`). Pusty katalog = karuzeli nie ma, karta wygląda jak dziś.

Decyzje Właściciela (2026-09-28):

| Pytanie | Decyzja |
|---|---|
| Skąd zdjęcia na produkcji | z panelu (wgraj → przenieś do „pokoje” → utwórz `-thumb`); `pokoje` na serwerze to **dowiązanie** do `dane/pokoje`, jak `uploads` |
| Gdzie karuzela | w karcie rezerwacji, nad formularzem (miejsce zakomentowanego TODO #37) |

## User Stories

### Story 1 — gość planuje nocleg

**Persona**: para szukająca noclegu po degustacji; przegląda stronę na telefonie.

1. Przewija do „Zarezerwuj nocleg w winnicy”. Pod nagłówkiem widzi pas miniatur pokoi.
   ```
   ┌─ Zarezerwuj nocleg w winnicy ───────────────┐
   │ ‹ [pokój 1] [pokój 2] [łazienka] ›           │
   │ Przyjazd [__]  Wyjazd [__]  Goście [2] [Szukaj]│
   └──────────────────────────────────────────────┘
   ```
   **Za kulisami**: `initPokojeKaruzela()` pobiera `data/pokoje.json` → `wsgi.zywe_pokoje()` →
   `galeria.pokoje()` listuje pary w `attached_assets/pokoje/`.
2. Przesuwa pas palcem (scroll-snap) albo strzałkami ‹ › (desktop).
3. Stuka w miniaturę → pełnoekranowy podgląd `{nazwa}.{ext}`, przewijanie między pokojami,
   zamknięcie wraca do karty. Formularz rezerwacji nietknięty.

> **Zmiana vs. stan obecny**: karta ma dziś tylko nagłówek, formularz i dopisek o Booking.com;
> w HTML leży zakomentowany szkic 3 zdjęć (`pokoj-01..03.jpg`), których nie ma w repo.

### Story 2 — Właściciel dodaje zdjęcie pokoju

**Persona**: Właściciel, panel moderacyjny na telefonie.

1. Galeria → „Wgraj zdjęcia…” → `uploads/salon.jpg`.
2. Zaznacza plik, „Przenieś do” → `attached_assets/pokoje` → `pokoje/salon.jpg`.
3. Zaznacza `pokoje/salon.jpg` → „Utwórz warianty: -thumb” → `pokoje/salon-thumb.jpg`.
4. Odświeża stronę — miniatura jest w karuzeli.

> Bez kroku 3 zdjęcie **nie** pojawi się w karuzeli (brak pary). `data/pokoje.json` zwraca je
> wtedy w `bez_miniatury`, żeby dało się to sprawdzić w przeglądarce.

### Przypadki brzegowe

| Sytuacja | Zachowanie |
|---|---|
| Katalog `pokoje/` nie istnieje albo pusty | `{"pokoje": [], ...}`, karuzela ukryta |
| `salon-thumb.jpg` bez `salon.*` | pominięte, nazwa w `bez_pelnego` |
| `salon.jpg` bez miniatury | pominięte, nazwa w `bez_miniatury` |
| `salon.jpg` i `salon.webp` + `salon-thumb.jpg` | pełne: najpierw to samo rozszerzenie co miniatura, potem `.jpg`, `.jpeg`, `.webp`, `.png` |
| Wariant `salon-sm.jpg` | ignorowany (to nie jest ani miniatura, ani pełne zdjęcie) |
| Jedno zdjęcie | karuzela bez strzałek |
| Motyw `dark` | strzałki i obramowania przez zmienne motywu |

## Architektura

| Warstwa | Zmiana |
|---|---|
| `galeria.py` | `KATALOGI_ZEWNETRZNE = ("uploads", "pokoje")` — oba mogą być dowiązaniami poza `attached_assets`; `_korzenie()` i `stan()` obejmują oba. `pokoje() -> dict` listuje pary. `usun()` bez zmian — tylko `uploads/`. |
| `wsgi.py` | `/data/pokoje.json` → `_json(galeria.pokoje())` (cienka trasa, GUARDRAILS #3). Wyjątek w `_plik()` z SPEC-009 rozszerzony na `KATALOGI_ZEWNETRZNE`. |
| `tools/dev-server.py` | ta sama trasa `/data/pokoje.json` (serwer lokalny serwuje statyki, katalogu nie wylistuje sam) |
| `index.html` | w karcie `#noclegi`: kontener karuzeli (`hidden`) zamiast zakomentowanego TODO zdjęć pokoi |
| `assets/js/main.js` | `initPokojeKaruzela()` w `DOMContentLoaded`; osobna instancja `GLightbox({ selector: ".pokoje-karuzela__link" })` |
| `assets/css/custom.css` | `.pokoje-karuzela*` — własne klasy, kolory przez `hsl(var(--…))` |
| `.gitignore` | `/attached_assets/pokoje` |

**Dlaczego nie `gallery-swiper`**: kod galerii „O nas” (`initGallerySwiperDots`, `syncCarouselToGallery`)
używa stałych id i **globalnego** `qsa(".gallery-swiper__dot")`, a GLightbox startuje z selektorem
`[data-glightbox]` na całej stronie. Te same klasy/atrybuty w pokojach wmieszałyby się w galerię
„O nas”. Linki pokoi **nie** mają atrybutu `data-glightbox`.

### Kontrakt `GET /data/pokoje.json`

```json
{
  "pokoje": [
    {"nazwa": "01-salon",
     "miniatura": "attached_assets/pokoje/01-salon-thumb.jpg",
     "pelne": "attached_assets/pokoje/01-salon.jpg"}
  ],
  "bez_miniatury": ["02-lazienka"],
  "bez_pelnego": []
}
```

Ścieżki względne od korzenia witryny — `main.js` dokleja `KORZEN`. Nazwy plików trafiają do
atrybutów, więc front-end używa DOM API (`setAttribute`, `textContent`), nie `innerHTML`.

## UI/UX

- Pas przewijany poziomo, `scroll-snap-type: x mandatory`; slajd `aspect-ratio: 3/4` jak w galerii
  „O nas" (1 zdjęcie mobile, 2 od 640px, 3 od 1024px), `rounded-md`, hover `scale(1.04)`.
- **Karuzela pokazuje duże zdjęcie (`pelne`), nie miniaturę** (zmiana 2026-10-01). Para `-thumb`
  jest jednak nadal wymagana po stronie serwera (`galeria.pokoje()`) — bez niej zdjęcie nie trafi
  do JSON-a. Zdjęcie bez `-thumb` nadal ląduje w `bez_miniatury`. Do decyzji: zdjąć to wymaganie.
- Kropki pod pasem (`#pokoje-karuzela-dots`, klasy `.pokoje-karuzela__dot*`): jak w „O nas",
  nadmiarowe chowane CSS-em (od 640px ostatnia, od 1024px dwie ostatnie); gdy wszystko mieści się
  naraz, kropki są ukryte (`hidden`). Pas i strzałki siedzą w `.pokoje-karuzela__okno`, żeby kropki
  nie przesuwały środka strzałek.
- Strzałki ‹ › (przyciski z `aria-label`) tylko, gdy jest co przewijać; ikony `#icon-chevron-left/right`.
- `alt` miniatury: „Pokój: {nazwa bez numeru i myślników}”.
- Obrazy `loading="lazy"`, `decoding="async"`.

## Wdrożenie

```bash
sudo mkdir -p /opt/apps/app_winnicakielnagora.pl/dane/pokoje
sudo chown winnicakielnagora:www-data /opt/apps/app_winnicakielnagora.pl/dane/pokoje
sudo chmod 750 /opt/apps/app_winnicakielnagora.pl/dane/pokoje
sudo -u winnicakielnagora ln -s /opt/apps/app_winnicakielnagora.pl/dane/pokoje \
  /opt/apps/app_winnicakielnagora.pl/app/attached_assets/pokoje
```

Panel przenosi tylko do **istniejącego** katalogu — bez tego kroku „pokoje” nie pojawi się na liście.
`/zdrowie` dostaje pole `"pokoje"` (jak `"uploads"`).

## Testy

- `tools/test-uploads.py` (lub nowy blok): `galeria.pokoje()` — para, brak miniatury, brak pełnego,
  preferencja rozszerzenia, ignorowanie `-sm`, kolejność, katalog-dowiązanie poza `attached_assets`.
- `tools/test-routing.py`: `attached_assets/pokoje/...` za dowiązaniem → 200; obce dowiązanie → 404.
- `tools/test-panel-auth.py`: `/zdrowie` ma `"pokoje"`.
- Przegląd w przeglądarce: karuzela z kilkoma zdjęciami, podgląd, oba motywy, szerokość telefonu.

## Implementation Checklist

- [x] **T1** Inject standards (← blokuje resztę)
- [x] **T2** `galeria.py`: `KATALOGI_ZEWNETRZNE`, `_korzenie()`/`stan()` na oba katalogi, `pokoje()` (← T1)
- [x] **T3** `wsgi.py`: `/data/pokoje.json`, `_plik()` dla obu katalogów, `/zdrowie` → `"pokoje"`; `dev-server.py`: `/data/pokoje.json` (← T2)
- [x] **T4** `index.html`: kontener karuzeli w karcie `#noclegi` (← T1)
- [x] **T5** `custom.css`: `.pokoje-karuzela*` (← T4)
- [x] **T6** `main.js`: `initPokojeKaruzela()` + GLightbox pokoi + rejestracja w `DOMContentLoaded` (← T3, T4)
- [x] **T7** `.gitignore`, `WDROZENIE.md`, README panelu (← T3)
- [x] **T8** Testy: `galeria.pokoje()`, routing za dowiązaniem, `/zdrowie` (← T2, T3)
- [ ] **T9** Weryfikacja standardów + przegląd w przeglądarce (dane testowe w scratchpadzie) (← T5–T8)
  — testy automatyczne przechodzą; przegląd wyglądu (oba motywy, telefon, podgląd GLightbox) robi Właściciel poza localhost

## Changelog

### 2026-09-28 (implementacja)
- T1–T8: `galeria.pokoje()`, `KATALOGI_ZEWNETRZNE`, `/data/pokoje.json` (wsgi + dev-server), `/zdrowie` → `pokoje`,
  karuzela w karcie `#noclegi`, testy. Standard `frontend/theming.md` opisuje 5 motywów — nieaktualny (są 2), do `/sync-standards`.

### 2026-09-28
- Pierwsza wersja specyfikacji.

### 2026-10-01
- Układ jak w galerii „O nas" (3:4, 1/2/3 kolumny, hover), duże zdjęcie zamiast miniatury, kropki.
