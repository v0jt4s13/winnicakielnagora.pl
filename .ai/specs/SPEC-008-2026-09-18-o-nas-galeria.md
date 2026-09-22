# SPEC-008 — O nas Gallery

**Status**: ✅ Wdrożone (2026-09-18)
**Rozmiar**: M+
**Owner**: kst
**Zależy od**: SPEC-002 (panel redakcyjny), SPEC-007 (galeria główna w panelu)

---

## Purpose

Galeria zdjęć sekcji „O nas" — responsywny swiper ze scroll-snap CSS, zarządzaniem w panelu redakcyjnym, i niezależnym magazynem plików (`assets/o_nas_galeria/`).

---

## Architecture

### Data Storage

- **Plik**: `data/o_nas_galeria.json`
- **Struktura**:
  ```json
  {
    "gallery": [
      {
        "path": "assets/o_nas_galeria/image.jpg",
        "title": "Opis (opcjonalnie)",
        "alt": "alt text (obowiązkowy)",
        "order": 1,
        "active": true
      }
    ]
  }
  ```
- **Wersja na produkcji**: poza katalogiem wdrożenia (`GALLERY_PATH` env var, patrz `o_nas_galeria.py`)
- **Wersja startowa w repo**: `data/o_nas_galeria.json` (seed na pierwszym uruchomieniu)

### File Storage

- **Katalog**: `assets/o_nas_galeria/`
- **Formaty**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
- **Polityka**:
  - Pliki są **niezależne** od głównej galerii zdjęć (`attached_assets/butelki/`, itp.)
  - Dodawanie: kopiowanie z głównej galerii z sufiksem jeśli duplikat (`image_1.jpg`, `image_2.jpg`)
  - Usuwanie: plik usuwany z dysku **dopiero przy zapisie JSON** (umożliwia anulowanie zmian)
  - Sierocze pliki: bezpieczne (zznajdą się w JSON przy następnym zapisie lub można je usunąć ręcznie)

**Dlaczego `assets/` zamiast `attached_assets/`?**
- `assets/` — zasoby strony (CSS, JS, fonty, grafiki finalne)
- `attached_assets/` — edytowalne źródła do galerii głównej (by nie dublować zdjęć na liście w panelu)
- Galeria O nas to część wizualnej zawartości strony, nie dane źródłowe — stąd `assets/`

### Backend (Python)

**Moduł**: `o_nas_galeria.py`

```python
# Funkcje
load()                      # Wczytaj JSON (lub skeleton jeśli brak)
validate(data)              # Walidacja struktury JSON
save(data)                  # Atomowy zapis na dysk + backup
save_safely(data, version)  # Zapis z detektorem konfliktu (dwie karty edytujące jednocześnie)
version_hash()              # SHA256 pliku na dysku (dla detektora konfliktów)
copy_image_with_suffix()    # Skopiuj plik z głównej galerii do o_nas/, z sufiksem jeśli duplikat
delete_image(path)          # Usuń plik z o_nas_galeria/ (bezpieczna — tylko te scieżki)
initial_state()             # Dane do wczytania do panelu na starcie
backup_info()               # Ścieżka do .bak kopii (dla UI panelu)
```

**Walidacja** (`validate()`):
- Wymaga: `path` (non-empty string), `title` (string, może być pusty), `alt` (non-empty string), `order` (positive int), `active` (boolean)
- Blokuje duplikaty `order`
- Nie sprawdza istnienia pliku na dysku (galerię widać w panelu zaraz po dodaniu, nawet jeśli fetch się wstrzymał)

**Atomic Write** (`save_safely()`):
- Lock file + fcntl na dysku
- Detekt konfliktów: jeśli plik się zmienił od ostatniego wczytania, reject (użytkownik musi refresh'nąć panel)
- Backup do `.bak`

### Backend Routes

#### Local Panel (`tools/panel/serwer.py`)

| Endpoint | Method | Opis |
|----------|--------|------|
| `/api/o-nas-galeria-wczytaj` | GET | Wczytaj aktualny stan galerii |
| `/api/o-nas-galeria-zapisz` | POST | Zapisz galerię na dysk (ze sprawdzeniem konfliktu + usuwaniem sierocych plików) |
| `/api/o-nas-galeria-dodaj-z-galerii` | POST | Skopiuj zaznaczone zdjęcia z głównej galerii do `o_nas_galeria/` |

#### Production (`wsgi.py`)

Identyczne endpointy, ale z HTTP Basic Auth (zmienne `PANEL_UZYTKOWNIK`, `PANEL_HASLO_HASH`).

**Logika usuwania plików**:
- Przy `/api/o-nas-galeria-zapisz`: porównaj starą galerię (z `bazowe_dane`) z nową
- Znalezione usunięte elementy → `delete_image()` dla każdego
- Jeśli plik już nie istnieje, nie ma błędu (idempotentne)

### Frontend (JavaScript)

#### `tools/panel/panel.js`

```javascript
// Stan
let oNasGaleria = [];                    // Aktualna galeria w pamięci
let oNasGaleriaBase = [];                // Stan sprzed zmian (dla detektu konfliktów)
let wersjaONasGaleria = "";              // SHA256 z serwera (dla detektu konfliktów)
let zmienioneONasGaleria = false;        // Flag "są niezapisane zmiany?"

// Główne funkcje
async function wczytajONasGaleria()                // GET /api/o-nas-galeria-wczytaj
async function zapiszONas()                        // POST /api/o-nas-galeria-zapisz
function potwierdzDodajDoONas()                    // POST /api/o-nas-galeria-dodaj-z-galerii
function renderListeONasGaleria()                  // Render listy w panelu
function normalizeOrderONas()                     // Renumeruj `order` od 1
function walidujONasGaleria(dane)                 // Walidacja w przeglądarce (przed wysłaniem)

// Eventy
#lista-o-nas change              → edycja checkboxa `active` lub pola `title`
#lista-o-nas click               → move-up/move-down/delete
#dodaj-do-o-nas click            → kopiuj zaznaczone z galerii głównej + auto-zapis JSON
#zapisz-o-nas click              → wysyłka JSON
#odrzuc-o-nas click              → anuluj zmiany (reset z `oNasGaleriaBase`)
```

**Panel UI** (`tools/panel/panel.html`):
- Sekcja „O nas (galeria)" — lista zdjęć z miniaturkami, checkboxem `Aktywne`, przyciskami ↑/↓, Usuń
- Pole edycji `title` — puste na starcie, opcjonalne
- Przycisk „+ Dodaj do O nas" — otwiera selektor z głównej galerii (`#galeria-grid`), kopiuje zaznaczone

**Zmiany na starcie dodawania**:
- `title` = `""` (puste, nie nazwa pliku)
- `active` = `false` (nie pokazywane na stronie, dopóki nie włączysz)
- `order` automatycznie — kolejny numer

**Auto-zapis po dodaniu**:
- Po pomyślnym skopiowaniu wzywa `zapiszONas()` (zapisuje JSON od razu)
- Umożliwia cofnięcie zmian przez refresh'nięcie strony bez strachu o sierocze pliki

#### `assets/js/main.js`

```javascript
async function loadGalleryFromJSON()     // Wczytaj JSON, filtruj active=true, renderuj
function initGallerySwiperDots()       // Dot navigation (guziki pod zdjęciami)
function updateNavButtonsVisibility()    // Ukryj ← button na pierwszym zdjęciu, → na ostatnim
function initGalleryGlightbox()          // GLightbox modal do przeglądania w pełnym ekranie
```

**Lifecycle**:
1. `DOMContentLoaded` → `loadGalleryFromJSON()`
2. Fetch `data/o_nas_galeria.json`
3. Filtruj `active === true`
4. Sortuj po `order`
5. Dynamiczny render `<img>` w carousel container
6. Wstawianie CTA boxa na koniec (przed dot navigation)
7. `initGallerySwiperDots()` — utworzenie guzików nawigacji
8. `initGalleryGlightbox()` — rejestracja modal zdjęć

**Carousel CSS** (`assets/css/custom-kst.css`):
- `aspect-ratio: 8/9` (mobile — jedno zdjęcie)
- `aspect-ratio: 16/9` (desktop ≥768px — dwa zdjęcia obok siebie)
- `scroll-snap-type: x mandatory` — smooth scroll
- `gap: 1rem` — padding między zdjęciami
- Padding `1rem` dookoła (responsywny na mobilach)

**Navigation buttons** (`#gallery-prev`, `#gallery-next`):
- Pozycja: `position: absolute` na obu stronach carousel'a
- Ukryte: `opacity: 0` na mobilach (`@media max-width: 767px`)
- Widoczność na desktop'ie: zależy od pozycji scroll'a
  - `#gallery-prev` pokazany jeśli `scrollLeft > 0` (nie jesteś na pierwszym)
  - `#gallery-next` pokazany jeśli `scrollLeft + clientWidth < scrollWidth` (nie jesteś na ostatnim)

**Dot navigation**:
- Jeden guzik = jedno zdjęcie (nie liczy się CTA box)
- Na mobilach: ostatni dot ukryty (`md:hidden`) bo box nie jest dostępny
- Na desktop'ie: ostatni dot też ukryty bo dwa ostatnie itemy są widoczne razem

**GLightbox integration**:
- `<a href="/assets/o_nas_galeria/image.jpg" data-glightbox>`
- CSS override `.goverlay` → full black tło
- Nav buttons `.gnext`, `.gprev` — taki sam rozmiar co carousel nav (3rem, zaokrąglone)

---

## Implementation Checklist

- [x] Backend: `o_nas_galeria.py` z load/save/validate/copy/delete
- [x] Routes: `/api/o-nas-galeria-wczytaj`, `-zapisz`, `-dodaj-z-galerii` (serwer + wsgi)
- [x] Panel HTML: sekcja O nas, lista zdjęć, pola edycji
- [x] Panel JS: wczytaj, zapisz, dodaj, edit, sort, delete, auto-save
- [x] Frontend: loadGalleryFromJSON, rendering carousel
- [x] CSS: aspect-ratio mobile/desktop, scroll-snap, nav button visibility
- [x] GLightbox: modal, CSS override, nav buttons
- [x] Dot navigation: sync carousel/glightbox, skip CTA box
- [x] Responsywność: 1 zdjęcie mobile, 2 desktop
- [x] Title edycja: puste na start, opcjonalne w panelu
- [x] Active toggle: pokazywanie/ukrywanie na stronie
- [x] Conflict detection: save_safely z version hash
- [x] Orphaned file cleanup: usuwanie plików gdy JSON zapisany
- [x] Copy with suffix: duplikaty obrazów

---

## Known Limitations & Non-Goals

1. **Brak resizing zdjęć** — bierze się oryginalne, ułożone w carousel'u
2. **Brak kategorii** — wszystkie zdjęcia w jednej galerii
3. **Brak filtru/search w panelu** — dodajesz ręcznie zaznaczając w głównej galerii
4. **Brak pagynacji** — wszystkie aktywne zdjęcia naraz (praktycznie: maks 10-20 dla UX)
5. **Brak drag-drop w panelu** — sortowanie tylko strzałkami ↑/↓
6. **Brak oryginału dla każdej wersji zdjęcia** — nie ma WebP + fallback JPG
7. **Alt text niezmienialny** — bierze się z nazwy pliku, można edytować ręcznie w JSON

---

## Browser Support

- Chrome/Edge: ✅ (scroll-snap, aspect-ratio)
- Firefox: ✅
- Safari: ⚠️ (scroll-snap może mieć różne zachowanie na iOS)
- IE: ❌

---

## Security

- ✅ Walidacja po stronie serwera (`o_nas_galeria.py`)
- ✅ Walidacja po stronie panelu (JS) — dla UX, nie dla bezpieczeństwa
- ✅ Wersjonowanie i detekcja konfliktów (`save_safely`)
- ✅ Atomic write (lock file + fcntl)
- ✅ Backup automatyczny (`.bak`)
- ✅ Panel tylko za hasłem na produkcji (HTTP Basic Auth)
- ✅ Kopiowanie bezpieczne — plik skopiowany dopiero gdy JSON zapisany; można cofnąć bez strachu
- ✅ Usuwanie bezpieczne — plik usuwany **po** zapisaniu JSON (nie na odwrót)

---

## Performance

- Galeria wczytywana przez `fetch` (może być cachowana)
- Lazy loading na zdjęciach (atrybut `loading="lazy"`)
- Dot navigation budowany za kazdym razem przy ładowaniu (szybkie dla maks 20 zdjęć)
- GLightbox ładowany z CDN (glightbox.min.js, glightbox.min.css)

---

## Dependencies

| Gdzie | Co | Dlaczego |
|-------|-----|----------|
| `assets/js/` | `glightbox.min.js` | Modal do przeglądania zdjęć w pełnym ekranie |
| `assets/css/` | `glightbox.min.css` | Style modalu GLightbox |
| `assets/css/` | `custom-kst.css` | Custom CSS carousel (aspect-ratio, scroll-snap, nav buttons) |
| Backend | Python 3.11 (stdlib) | fcntl, json, pathlib, hashlib, shutil |

**Brak**: jQuery, Bootstrap, React, Tailwind na carousel (używamy vanilla CSS + scroll-snap)

---

## Testing

### Manual (Browser)

- [ ] Otwórz `/` lokalnie (`python3 tools/dev-server.py --port 5000`)
- [ ] Sekcja O nas wyświetla galerię (mobile: 1 zdjęcie, desktop: 2)
- [ ] Dot navigation zsynchronizowana z carousel'em
- [ ] Nav buttons (← →) pojawiają się/znikają wg pozycji scroll'a
- [ ] GLightbox otwiera się na klik zdjęcia
- [ ] W dwóch motywach: `classic`, `dark` — brak błędów CSS
- [ ] Bez konsoli JS błędów

### Panel

- [ ] Wczytanie: `GET /api/o-nas-galeria-wczytaj` zwraca galerię
- [ ] Dodawanie: zaznacz zdjęcia w głównej galerii, kliknij „+ Dodaj do O nas"
  - [ ] Pliki skopiowane do `assets/o_nas_galeria/`
  - [ ] JSON zapisany z `active: false`
  - [ ] Checkboxy w galerii głównej odznaczone
- [ ] Edycja: zmień `title`, `active` lub kolejność
- [ ] Zapis: kliknij „Zapisz"
  - [ ] JSON na dysku ze zmianami
  - [ ] Usunięte zdjęcia — pliki usunięte z dysku
- [ ] Konflikt: otwórz panel w dwóch kartach, edytuj w jednej, zapisz w drugiej
  - [ ] Druga karta dostanie `409 Conflict`
  - [ ] Panel powinien refresh'nąć stan
- [ ] Odrzucenie: kliknij „Odrzuć zmiany"
  - [ ] Galeria wraca do stanu sprzed edycji
  - [ ] Pliki **pozostają** na dysku (jeśli były dodane bez zapisu)

### Automated

```bash
python3 tools/test-routing.py          # routing + publiczne pliki
# (nie ma dedykowanego test-o-nas-galeria.py, ale walidacja JSON jest w test-cennik-sciezka.py pattern'e)
```

---

## Changelog

### 2026-09-18
- Wdrożona całkowita galeria O nas: backend (copy, delete, save_safely), panel (add, edit, sort, delete), frontend (carousel, dots, nav buttons, glightbox)
- Dodana automatyczna synchronizacja z główną galerią (copy images with suffix)
- Implementacja detekcji konfliktów i wersjonowania pliku
- Auto-zapis JSON po dodaniu zdjęć (umożliwia bezpieczne cofnięcie zmian)
