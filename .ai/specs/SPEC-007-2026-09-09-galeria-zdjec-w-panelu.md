# SPEC-007 - Galeria zdjęć w panelu redakcyjnym

**Status**: zaimplementowane
**Rozmiar**: M
**Data**: 2026-09-09
**Zależy od**: SPEC-002 - panel redakcyjny

## Overview

Panel redakcyjny dostaje galerię plików graficznych z całego katalogu
`attached_assets/`. Właściciel może przeglądać obrazy pogrupowane według katalogów,
otwierać większy podgląd, przenosić obrazy do istniejących katalogów oraz tworzyć
warianty zoptymalizowane do użycia na stronie.

Galeria nie zmienia danych produktów automatycznie. Pole `zdjecie` i opcjonalne
`zdjecie_sklep` pozostają edytowane w cenniku, a operacje plikowe są natychmiastowe
na dysku i wymagają osobnego commitu lub wdrożenia.

## User Stories

### Story 1 - przeglądanie i podgląd

Właściciel otwiera sekcję „Galeria zdjęć”, wybiera katalog lub „Wszystkie katalogi”
i widzi karty z obrazami, nazwami plików, rozmiarem i wymiarami. Kliknięcie obrazu
otwiera większy podgląd bez opuszczania panelu.

**Za kulisami**: `GET /api/galeria-wczytaj` zwraca wyłącznie obrazy znajdujące się
pod `attached_assets/`. Ścieżki są względne względem tego katalogu i nie są składane
z danych użytkownika bez ponownej walidacji.

### Story 2 - przenoszenie obrazów

Właściciel zaznacza jeden lub kilka obrazów, wybiera katalog docelowy i klika
„Przenieś”. Panel odświeża galerię i pokazuje komunikat z liczbą przeniesionych plików.
Istniejący plik o tej samej nazwie nie jest nadpisywany, a operacja zostaje odrzucona
z czytelnym komunikatem.

**Za kulisami**: `POST /api/galeria-przenies` przyjmuje `{ "pliki": [...],
"katalog": "photos/hero" }`. Serwer rozwiązuje ścieżki przez `resolve()` i wymaga,
by źródło i cel pozostały wewnątrz `attached_assets/`; katalog docelowy musi już istnieć.

### Story 3 - tworzenie wariantów

Właściciel zaznacza obrazy, wybiera `-sm`, `-thumb` albo oba warianty i klika
„Utwórz warianty”. `-sm` ma dłuższy bok 600 px, a `-thumb` 300 px. Pliki trafiają
do tego samego katalogu i zachowują rozszerzenie źródła. Istniejące warianty są
pomijane, nie nadpisywane.

**Za kulisami**: `POST /api/galeria-warianty` przyjmuje `{ "pliki": [...],
"warianty": ["sm", "thumb"] }`. Obrazy są obracane zgodnie z EXIF, przeskalowywane
przez Pillow i zapisywane atomowo. Brak Pillow zwraca komunikat konfiguracji, bez
wyłączania pozostałej funkcji panelu.

## Architektura

```text
tools/panel/panel.html + panel.js + panel.css
              │
              ├── GET /api/galeria-wczytaj
              ├── POST /api/galeria-przenies
              └── POST /api/galeria-warianty
                            │
                       galeria.py
                            │
                    attached_assets/
```

`galeria.py` jest wspólną warstwą dla lokalnego `tools/panel/serwer.py` i
produkcyjnego `wsgi.py`, dzięki czemu walidacja ścieżek i format operacji są takie same.
Panel lokalny nadal wymaga `127.0.0.1` i nagłówka `Origin`, a produkcyjny endpoint
pozostaje za istniejącym Basic Auth.

## API

### `GET /api/galeria-wczytaj`

```json
{
  "katalogi": ["", "butelki", "photos", "photos/age-restriction"],
  "pliki": [
    {
      "sciezka": "butelki/nazwa.jpg",
      "katalog": "butelki",
      "nazwa": "nazwa.jpg",
      "rozmiar": 123456,
      "szerokosc": 4080,
      "wysokosc": 2296
    }
  ]
}
```

Lista obejmuje rozszerzenia `.jpg`, `.jpeg`, `.png`, `.webp` i `.gif`, sortowane
według katalogu i nazwy. Katalog główny `attached_assets/` ma pustą ścieżkę.

### `POST /api/galeria-przenies`

```json
{ "pliki": ["butelki/nazwa.jpg"], "katalog": "photos" }
```

Sukces: `{ "ok": true, "przeniesiono": 1 }`.

### `POST /api/galeria-warianty`

```json
{ "pliki": ["butelki/nazwa.jpg"], "warianty": ["sm", "thumb"] }
```

Sukces zwraca liczbę utworzonych i pominiętych plików. Każdy wariant ma nazwę
`<nazwa-bez-sufiksu>-sm.ext` albo `...-thumb.ext`.

## Bezpieczeństwo i błędy

- Żaden endpoint nie przyjmuje ścieżki absolutnej, `..`, dowiązania wychodzącego poza
  `attached_assets` ani katalogu docelowego, który nie istnieje.
- Operacje dotyczą wyłącznie plików graficznych. Panel nie udostępnia przez galerię
  plików tekstowych, danych ani kodu.
- Przenoszenie nie nadpisuje celu. Tworzenie wariantów nie nadpisuje istniejących plików.
- Błędy walidacji wracają jako HTTP 400, błędy uprawnień lub Pillow jako HTTP 500 z
  komunikatem dla operatora.

## UI/UX

- Sekcja galerii jest niezależna od niezapisanych zmian cennika i wydarzeń.
- Filtr katalogu, zaznaczanie wielu kart, wybór katalogu docelowego i wybór wariantów
  są dostępne bez użycia `alert()` lub `confirm()`.
- Karta pokazuje miniaturę obrazu, nazwę, katalog, wymiary i rozmiar pliku.
- Na wąskim ekranie akcje zawijają się, a siatka przechodzi na jedną kolumnę.

## Implementation Checklist

- [x] `galeria.py` - bezpieczne listowanie, przenoszenie i generowanie wariantów
- [x] `tools/panel/serwer.py` - lokalne endpointy i statyki `attached_assets`
- [x] `wsgi.py` - zabezpieczone endpointy produkcyjne
- [x] `panel.html`, `panel.css`, `panel.js` - galeria, podgląd i akcje
- [x] testy bezpieczeństwa ścieżek, przenoszenia i wariantów
- [x] aktualizacja README panelu

## Changelog

### 2026-09-09
- Pierwsza specyfikacja galerii zdjęć i operacji na plikach w `attached_assets/`.
- Zaimplementowano galerię, przenoszenie plików i warianty `-sm` oraz `-thumb`.
