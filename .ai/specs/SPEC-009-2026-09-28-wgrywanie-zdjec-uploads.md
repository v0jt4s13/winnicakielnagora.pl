# SPEC-009 — Wgrywanie zdjęć do `attached_assets/uploads/` z panelu

Rozmiar: **L** (nowa ścieżka zapisu plików binarnych na produkcji + zależność Pillow).
Rozszerza SPEC-007 (galeria zdjęć w panelu).

## Overview

Właściciel wgrywa zdjęcia z komputera lub telefonu przez panel moderacyjny. Pliki trafiają do
`attached_assets/uploads/`, są zmniejszane i pozbawiane metadanych, a potem widoczne w istniejącej
galerii panelu (SPEC-007): podgląd, warianty `-sm`/`-thumb`, „Użyj jako zdjęcia produktu w sklepie”,
dodanie do wydarzenia. Nowa operacja **usuń** działa wyłącznie na plikach w `uploads/` i odmawia
usunięcia zdjęcia, którego używa cennik albo wydarzenie.

Decyzje Właściciela (2026-09-28):

| Pytanie | Decyzja |
|---|---|
| Gdzie leżą pliki na produkcji | `attached_assets/uploads` jest **dowiązaniem symbolicznym** do `/opt/apps/app_winnicakielnagora.pl/dane/uploads` — poza katalogiem z gitem, deploy go nie kasuje |
| Obróbka przy wgrywaniu | zmniejszenie (dłuższy bok ≤ 2000 px) + usunięcie EXIF (GPS, model aparatu) przez Pillow |
| Usuwanie | tak, **tylko** z `uploads/`, z blokadą zdjęć używanych w `data/wina.json` i `data/wydarzenia.json` |

Pillow był dotąd opcjonalny (tylko warianty). Ta funkcja go **wymaga** — zgoda Właściciela na
zależność (GUARDRAILS BLOCK #6) jest powyższą decyzją. Brak Pillow = czytelny komunikat, reszta
panelu działa.

## User Stories

### Story 1 — Właściciel wgrywa zdjęcia z telefonu

**Persona**: Właściciel winnicy, nietechniczny. Zrobił telefonem zdjęcia nowych butelek i chce
ich użyć w cenniku bez pośrednictwa programisty.

1. Otwiera panel na telefonie → sekcja „Galeria zdjęć” → przycisk „Wgraj zdjęcia”.
   ```
   ┌─ Galeria zdjęć (42 obrazów) ─────────────────────────────┐
   │ [Wgraj zdjęcia…]  JPG, PNG, WebP · do 15 MB na plik       │
   │ Katalog: [Wszystkie katalogi ▾]                           │
   └───────────────────────────────────────────────────────────┘
   ```
2. Wybiera 3 zdjęcia (≈ 6 MB każde). Pod przyciskiem pojawia się postęp: `Wgrywam 2 z 3…`.
   **Za kulisami**: `panel.js` wysyła każdy plik osobnym `POST api/galeria-wgraj?nazwa=<oryginał>`
   z surowymi bajtami w ciele (bez multipart). Serwer: limit rozmiaru → Pillow otwiera obraz →
   `exif_transpose` → `thumbnail(2000)` → zapis bez metadanych do `uploads/<slug>.jpg` (atomowo,
   bez nadpisywania — przy kolizji `-2`, `-3`…).
3. Komunikat: `✓ Wgrano 3 zdjęcia do attached_assets/uploads/`. Galeria przełącza filtr na
   `attached_assets/uploads` i pokazuje nowe karty (≈ 400 KB, 2000 × 1500 px).
4. Na karcie klika „Użyj jako zdjęcia produktu w sklepie” — istniejąca akcja SPEC-007, bez zmian.

> **Zmiana vs. stan obecny**: dziś zdjęcie trafia do `attached_assets/` tylko przez commit
> programisty. Po zmianie — przez panel, w kilka sekund, bez gita.

### Story 2 — Właściciel sprząta nieudane zdjęcia

**Persona**: ten sam Właściciel; wgrał przez pomyłkę rozmazane zdjęcie i jego kopię.

1. Filtr `attached_assets/uploads`, zaznacza dwa pliki → „Usuń zaznaczone”.
2. Panel pyta inline (nie `confirm()` — GUARDRAILS): `Usunąć 2 pliki? Tego nie da się cofnąć. [Usuń] [Anuluj]`.
3. Jeden z plików jest ustawiony jako `zdjecie_sklep` wina „Monarch 2022”:
   ```
   ✗ Nie usunięto nic. uploads/monarch-butelka.jpg jest używane:
     • cennik: Monarch (monarch-2022)
   ```
   **Za kulisami**: `POST api/galeria-usun {pliki:[…]}` — serwer sprawdza **wszystkie** pliki
   przed usunięciem **któregokolwiek** (operacja wszystko-albo-nic).
4. Odznacza używany plik, usuwa drugi → `✓ Usunięto 1 plik`.

> **Zmiana vs. stan obecny**: galeria nie ma dziś usuwania. Pliki spoza `uploads/` (hero, logo,
> zdjęcia odmian) nadal są nieusuwalne z panelu — przycisk jest nieaktywny, gdy zaznaczenie
> zawiera choć jeden taki plik.

### Story 3 — przypadki brzegowe

| Sytuacja | Zachowanie |
|---|---|
| Plik > 15 MB | 413 przed odczytem ciała, komunikat „Plik jest większy niż 15 MB” |
| `.jpg`, który nie jest obrazem (np. PDF z podmienionym rozszerzeniem) | Pillow nie otwiera → 400 „To nie jest obraz JPG, PNG ani WebP” |
| Obraz > 50 Mpx (bomba dekompresyjna) | 400, bez pełnego dekodowania |
| PNG z przezroczystością | zapis jako `.webp` z kanałem alfa; bez przezroczystości → `.jpg` |
| Nazwa `Zdjęcie 1 (kopia).JPG` | `zdjecie-1-kopia.jpg` |
| Brak Pillow na serwerze | 500 „Wgrywanie wymaga biblioteki Pillow na serwerze”, reszta panelu działa |
| Katalog `uploads` nie istnieje (świeży klon) | tworzony przy pierwszym wgraniu lokalnie; na produkcji brak dowiązania = komunikat z instrukcją z `WDROZENIE.md` |
| Przeniesienie pliku z `uploads/` do `photos/` (akcja SPEC-007) | dozwolone; plik przestaje być usuwalny z panelu |

## Architektura

### Dozwolone korzenie ścieżek

Trzy miejsca sprawdzają dziś „czy ścieżka leży w `attached_assets`” przez
`resolve()` + `is_relative_to(attached_assets.resolve())`: `galeria._wzgledna`/`stan`,
`cennik.sciezka_zdjecia_sklep`, walidacja `zdjecia` w `wydarzenia.waliduj`. Na produkcji
`uploads` rozwiązuje się do `dane/uploads`, czyli **poza** `attached_assets` — wszystkie trzy by
go odrzuciły. Dodatkowo `Path.rglob` w Pythonie 3.11 nie wchodzi do katalogów-dowiązań.

Rozwiązanie — jedna funkcja w `galeria.py`, używana przez wszystkie trzy moduły:

```python
UPLOADS = ZASOBY / "uploads"

def w_zasobach(sciezka_wzgledna: str) -> Path | None:
    """Plik pod attached_assets/ po walidacji leksykalnej (bez ., .., \\, NUL, ścieżek
    absolutnych); po resolve() musi leżeć w ZASOBY.resolve() albo UPLOADS.resolve()."""
```

- Ścieżka **względna** zwracana do przeglądarki liczona jest leksykalnie (`uploads/x.jpg`),
  nigdy z `resolve()`.
- `stan()` przechodzi `ZASOBY.rglob` jak dziś **plus** jawnie `UPLOADS.rglob`, gdy `UPLOADS`
  jest dowiązaniem.
- Serwowanie publiczne: `wsgi._plik()` po `resolve()` wymagał pliku wewnątrz `STATIC_ROOT`,
  więc plik za dowiązaniem `uploads` dostawał 404 (błąd pierwszej wersji tego specu, który
  zakładał „bez zmian”). `_plik()` ma jeden wyjątek: ścieżka leksykalnie
  `attached_assets/uploads/…`, plik po `resolve()` w rozwiniętym `uploads/`. Inne dowiązania
  poza repo — nadal 404 (`tools/test-routing.py`, `sprawdz_uploads_dowiazanie`).

### Moduł i trasy

| Warstwa | Zmiana |
|---|---|
| `galeria.py` | `UPLOADS`, `w_zasobach()`, `wgraj(nazwa, dane: bytes) -> dict`, `usun(pliki, uzycia) -> int`, `stan()` z dowiązaniem |
| `cennik.py`, `wydarzenia.py` | walidacja ścieżek przez `galeria.w_zasobach()` |
| `wsgi.py` | trasy panelu `galeria-wgraj`, `galeria-usun` (za Basic Auth, jak reszta panelu); limit rozmiaru per trasa |
| `tools/panel/serwer.py` | te same dwie trasy; `do_POST` z osobnym limitem dla `galeria-wgraj` |
| `panel.html/.js/.css` | przycisk „Wgraj zdjęcia…” (`<input type=file multiple accept>`), postęp, „Usuń zaznaczone” z potwierdzeniem inline |
| `.gitignore` | `attached_assets/uploads/` |

`wgraj()` i `usun()` nie znają HTTP (jak `cennik.py`, GUARDRAILS boundary #3 — `wsgi.py` tylko
woła i oddaje wynik).

**Kto liczy „użycia”**: `usun()` dostaje od trasy zbiór ścieżek używanych, zbudowany z
`cennik.wczytaj()` (`zdjecie_sklep`) i `wydarzenia.wczytaj()` (`zdjecia`). `o_nas_galeria` nie
wchodzi — kopiuje obraz do `assets/o_nas_galeria/`, więc nie odwołuje się do `uploads/`.
Pole `zdjecie` (slug) cennika i wydarzeń wskazuje wyłącznie `photos/<slug>.jpg`, więc nie może
dotyczyć `uploads/`.

### Limit rozmiaru żądania (produkcja)

`wsgi.py` ma globalnie `MAX_CONTENT_LENGTH = kontakt.MAX_CIAZAR_ZADANIA` (16 KB) — każdy upload
dostałby 413. Zmiana: globalny limit = `galeria.MAX_WGRYWANIE` (15 MB). `/api/contact` już dziś
sam sprawdza `request.content_length > MAX_CIAZAR_ZADANIA` (wsgi.py, trasa kontaktu) — zostaje
jako jedyna publiczna trasa POST i zachowuje swój limit. Trasy panelu są za hasłem.
Test: `tools/test-routing.py` / `test-contact.py` muszą nadal odrzucać > 16 KB na `/api/contact`.

## API

### `POST …/api/galeria-wgraj?nazwa=<nazwa-oryginalna>`

Ciało: surowe bajty pliku, `Content-Type: application/octet-stream`, maks. 15 MB.

- 200 `{"ok": true, "sciezka": "uploads/zdjecie-1.jpg", "szerokosc": 2000, "wysokosc": 1500, "rozmiar": 412345}`
- 400 `{"ok": false, "komunikat": "…"}` — nie obraz, format spoza JPG/PNG/WebP, > 50 Mpx, pusta nazwa
- 413 — za duży
- 500 — brak Pillow albo brak prawa zapisu (komunikat podaje ścieżkę, jak przy cenniku)

### `POST …/api/galeria-usun`

Ciało: `{"pliki": ["uploads/a.jpg", …]}` (1–200).

- 200 `{"ok": true, "usunieto": 2}`
- 400 `{"ok": false, "komunikat": "…", "uzycia": {"uploads/a.jpg": ["cennik: Monarch (monarch-2022)"]}}`
  — plik spoza `uploads/`, nie istnieje, albo jest używany. Nic nie zostaje usunięte.

## Bezpieczeństwo

- Typ pliku ustala **Pillow** (`Image.open` + `format in {"JPEG","PNG","WEBP"}`), nie rozszerzenie
  ani `Content-Type`. Wynik jest zawsze **ponownie zakodowany** — żadne bajty wejściowe nie trafiają
  na dysk bez przejścia przez dekoder.
- `Image.MAX_IMAGE_PIXELS = 50_000_000` przed otwarciem; `DecompressionBombError` → 400.
- Nazwa: tylko `[a-z0-9-]` (transliteracja PL jak `proponujId`), max 80 znaków, rozszerzenie
  nadaje serwer. Zapis przez `tempfile.mkstemp` w katalogu docelowym + `os.link`/`O_EXCL`,
  żeby dwa równoległe wgrania nie nadpisały się nawzajem.
- Metadane: zapis bez `exif=`, `icc_profile` zachowany (kolory), GPS/model/data znikają.
- Usuwanie: wyłącznie pliki, których ścieżka leksykalnie zaczyna się od `uploads/` **i** po
  `resolve()` leży w `UPLOADS.resolve()`.
- Prawa plików `0o644`, jak warianty `-sm`/`-thumb` w galerii — obrazy są publiczne
  (zmiana względem pierwszej wersji specu, która podawała `0o640` jak cennik).

## Konfiguracja i wdrożenie

Jednorazowo na serwerze (dopisać do `WDROZENIE.md`):

```bash
sudo mkdir -p /opt/apps/app_winnicakielnagora.pl/dane/uploads
sudo chown winnicakielnagora:www-data /opt/apps/app_winnicakielnagora.pl/dane/uploads
sudo chmod 750 /opt/apps/app_winnicakielnagora.pl/dane/uploads
ln -s /opt/apps/app_winnicakielnagora.pl/dane/uploads /opt/apps/app_winnicakielnagora.pl/app/attached_assets/uploads
# Pillow w środowisku aplikacji, jeśli go nie ma:
/opt/apps/app_winnicakielnagora.pl/venv/bin/pip install Pillow   # ścieżkę venv potwierdzić na serwerze
```

Otwarte do potwierdzenia na serwerze: (1) czy `production_manager.sh update` nie usuwa
nieśledzonych plików/dowiązań w `app/` (`git clean`) — jeśli tak, dowiązanie trzeba odtwarzać
w kroku `update`; (2) nginx musi pozwalać na ciało do 15 MB (`client_max_body_size 16m` w bloku
prefiksu) — domyślne 1 MB da 413 z nginx, zanim żądanie dotrze do aplikacji.

Brak nowych zmiennych środowiskowych.

## UI/UX

- Przycisk „Wgraj zdjęcia…” w pasku akcji galerii; wybór wielu plików; na telefonie `accept="image/*"`
  otwiera aparat/galerię.
- Wgrywanie sekwencyjne (jeden plik naraz) z licznikiem; błąd jednego pliku nie przerywa reszty —
  podsumowanie: `Wgrano 2 z 3. Nie wgrano: x.heic — to nie jest obraz JPG, PNG ani WebP`.
- „Usuń zaznaczone” aktywny tylko, gdy **wszystkie** zaznaczone pliki są w `uploads/`.
- Potwierdzenie usunięcia inline w pasku akcji, bez `confirm()`.
- Kolory wyłącznie przez zmienne panelu (`var(--…)`), jasny i ciemny wariant panelu.

## Testy

Nowy `tools/test-uploads.py` (tymczasowy katalog jako `attached_assets`, wzór `test-galeria.py`):

- wgranie JPG z EXIF GPS → plik bez EXIF, dłuższy bok ≤ 2000
- PNG z alfą → `.webp`; PNG bez alfy → `.jpg`
- PDF przemianowany na `.jpg` → odrzucony; > 50 Mpx → odrzucony
- kolizja nazw → `-2`
- nazwa `../../etc/x.jpg`, `a\\b.jpg`, NUL → slug bez ścieżki
- usuwanie: plik spoza `uploads/` odrzucony; plik używany odrzucony i **nic** nie usunięte; zwykły usunięty
- `uploads` jako dowiązanie poza `attached_assets`: `stan()` go listuje, `w_zasobach()` akceptuje,
  walidacja `cennik` i `wydarzenia` przyjmuje `uploads/x.jpg`, a dowiązanie do `/etc` — odrzuca

Istniejące: `test-galeria.py`, `test-routing.py`, `test-panel-auth.py` (nowe trasy za hasłem,
404 bez konfiguracji), `test-contact.py` (limit 16 KB na `/api/contact` nadal działa).

## Implementation Checklist

Zależności w nawiasach — zadanie startuje dopiero, gdy wskazane są odhaczone.

- [x] **T1** Inject standards (blokuje wszystkie pozostałe) — `backend/edycja-wspolbiezna`,
  `frontend/styling`, `frontend/js-conventions`; `backend/panel-fetch-sciezki` jest w `index.yml`,
  ale pliku brak — obowiązuje reguła z opisu w indeksie (fetch w `panel.js` względny)
- [x] **T2** `galeria.py`: `UPLOADS`, `w_zasobach()`, ścieżki względne liczone leksykalnie, `stan()` listuje dowiązane `uploads/` (← T1)
- [x] **T3** `cennik.py` (`sciezka_zdjecia_sklep`) i `wydarzenia.py` (walidacja `zdjecia`) przez `galeria.w_zasobach()` (← T2)
- [x] **T4** `galeria.py`: `MAX_WGRYWANIE`, `wgraj(nazwa, dane)` — Pillow, limit Mpx, `exif_transpose`, `thumbnail(2000)`, JPG/WebP bez EXIF, slug, zapis bez nadpisywania (← T2)
- [x] **T5** `galeria.py`: `usun(pliki, uzycia)` wszystko-albo-nic + budowanie `uzycia` z cennika i wydarzeń (← T2, T3)
- [x] **T6** `tools/panel/serwer.py`: trasy `galeria-wgraj` (osobny limit ciała) i `galeria-usun` (← T4, T5)
- [x] **T7** `wsgi.py`: trasy `galeria-wgraj`, `galeria-usun` za Basic Auth; `MAX_CONTENT_LENGTH` = `galeria.MAX_WGRYWANIE` (← T4, T5)
- [x] **T8** `panel.html/.js/.css`: „Wgraj zdjęcia…”, postęp, podsumowanie błędów, „Usuń zaznaczone” z potwierdzeniem inline (← T6)
- [x] **T9** `.gitignore` (`attached_assets/uploads/`) + `WDROZENIE.md` (katalog, dowiązanie, Pillow, `client_max_body_size`) + `tools/panel/README.md` (← T7)
- [x] **T10** `tools/test-uploads.py` + przebieg wszystkich `tools/test-*.py` i `node tools/test-produkty.js` (← T3–T7)
- [x] **T11** `/verify-standards` + podgląd panelu w przeglądarce: wgranie, użycie w produkcie, usunięcie (← T8–T10)
  — skill niedostępny w sesji, standardy sprawdzone ręcznie (fetch względny, qs/qsa, bez alert/confirm,
  kolory przez zmienne). API sprawdzone end-to-end na `serwer.py` i na prawdziwym Flasku (venv tymczasowy).
  Panel w headless Chrome ładuje się bez błędów konsoli. **Nie sprawdzono**: klikania „Wgraj zdjęcia…”
  z oknem wyboru plików i potwierdzenia usuwania w UI — do obejrzenia ręcznie.

## Changelog

### 2026-09-28 (poprawka po wdrożeniu)
- Pliki w `uploads/` na produkcji dawały 404 mimo udanego wgrania: `wsgi._plik()` odrzucał
  ścieżki rozwiązane poza `STATIC_ROOT`. Dodany wyjątek dla `attached_assets/uploads/` + test
  z dowiązaniem w `test-routing.py`. Testy na prawdziwym Flasku wcześniej używały zwykłego
  katalogu, nie dowiązania — dlatego tego nie złapały.

### 2026-09-28 (implementacja)
- Zaimplementowano T2–T10: `galeria.w_zasobach()`/`uploads()`, `wgraj()`, `usun()`,
  `uzycia_zdjec()`, trasy w `serwer.py` i `wsgi.py`, UI panelu, `tools/test-uploads.py`.
- `uploads` liczone funkcją od bieżącego `ZASOBY` (nie stałą) — testy podmieniają `ZASOBY`.
- `przenies()` obsługuje przeniesienie między systemami plików (EXDEV), bo `dane/uploads`
  może leżeć na innym montowaniu niż `attached_assets`.
- Prawa plików `0o644` zamiast `0o640`.

### 2026-09-28
- Pierwsza wersja specyfikacji: wgrywanie do `uploads/`, obróbka Pillow, usuwanie z blokadą użyć,
  dowiązanie `uploads → dane/uploads` na produkcji.
