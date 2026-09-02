"""Cennik win — odczyt, walidacja i zapis `data/wina.json`.

Wspolny modul dla dwoch wejsc:
  * `tools/panel/serwer.py` — panel uruchamiany lokalnie,
  * `wsgi.py` — panel na produkcji, za haslem.

Dzieki temu obie drogi walidują dane dokladnie tak samo. Modul nie zna HTTP
i niczego nie serwuje — same dane.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent
ZDJECIA = PROJEKT / "attached_assets" / "photos"
STRONY_ODMIAN = PROJEKT / "wina"

# Wersja startowa, wersjonowana w repozytorium. Na produkcji sluzy tylko do zasiania
# pliku roboczego przy pierwszym uruchomieniu.
CENNIK_W_REPO = PROJEKT / "data" / "wina.json"

# Zywy cennik. Na produkcji wskaz go POZA katalog wdrozenia (CENNIK_SCIEZKA), zeby
# kolejny deploy nie nadpisal cen wpisanych przez panel — decyzja Wlasciciela
# z 2026-09-02, wariant A z TODO #26. Lokalnie zostaje plik z repozytorium.
CENNIK = Path(os.environ.get("CENNIK_SCIEZKA") or CENNIK_W_REPO).expanduser()
KOPIA = CENNIK.with_suffix(CENNIK.suffix + ".bak")


def zapewnij_plik() -> None:
    """Przy pierwszym uruchomieniu kopiuje wersje z repozytorium na sciezke robocza.

    Bez tego panel na swiezym serwerze wystartowalby z pustym cennikiem, mimo ze
    w repozytorium jest gotowa lista win.
    """
    if CENNIK.exists() or CENNIK == CENNIK_W_REPO:
        return
    CENNIK.parent.mkdir(parents=True, exist_ok=True)
    if CENNIK_W_REPO.exists():
        CENNIK.write_bytes(CENNIK_W_REPO.read_bytes())

SZKIELET = {"waluta": "PLN", "stawka_vat": 0.23, "kategorie": [], "wina": []}

# Wlasciciel i grupa moga czytac, reszta nie. Grupa to zwykle www-data.
PRAWA_PLIKU = 0o640

POLA_WYMAGANE = ("id", "nazwa", "odmiana_slug", "kategoria", "pojemnosc_ml",
                 "cena_brutto", "rabat_procent", "dostepne", "opis", "zdjecie")
POLA_OPCJONALNE = ("rocznik", "alkohol")
WZOR_ID = re.compile(r"^[a-z0-9-]+$")


def slugi_zdjec() -> list[str]:
    """Slugi bez rozszerzenia i bez wariantow -sm — tak jak wyglada pole `zdjecie`."""
    if not ZDJECIA.is_dir():
        return []
    return sorted(p.stem for p in ZDJECIA.glob("*.jpg") if not p.stem.endswith("-sm"))


def slugi_odmian() -> list[str]:
    if not STRONY_ODMIAN.is_dir():
        return []
    return sorted(p.stem for p in STRONY_ODMIAN.glob("*.html"))


def wczytaj() -> dict:
    """Zwraca cennik. Gdy pliku nie ma — szkielet, ale go nie tworzy."""
    if not CENNIK.exists():
        return dict(SZKIELET)
    return json.loads(CENNIK.read_text(encoding="utf-8"))


def _blad(pozycja, pole, komunikat) -> dict:
    return {"pozycja": pozycja, "pole": pole, "komunikat": komunikat}


def waliduj(dane) -> list[dict]:
    """Lista bledow; pusta oznacza dane gotowe do zapisu.

    Serwer jest instancja rozstrzygajaca — przegladarce nie ufamy nawet lokalnie.
    """
    bledy: list[dict] = []
    if not isinstance(dane, dict):
        return [_blad(None, None, "Oczekiwano obiektu JSON")]

    kategorie = dane.get("kategorie")
    if not isinstance(kategorie, list) or not kategorie:
        bledy.append(_blad(None, "kategorie", "Lista kategorii nie może być pusta"))
        kategorie = []

    stawka = dane.get("stawka_vat")
    if not isinstance(stawka, (int, float)) or not 0 <= stawka < 1:
        bledy.append(_blad(None, "stawka_vat", "Stawka VAT musi być ułamkiem, np. 0.23"))

    wina = dane.get("wina")
    if not isinstance(wina, list):
        return bledy + [_blad(None, "wina", "Brak listy win")]

    dostepne_zdjecia, dostepne_odmiany = slugi_zdjec(), slugi_odmian()
    widziane_id: set[str] = set()

    for i, wino in enumerate(wina):
        if not isinstance(wino, dict):
            bledy.append(_blad(i, None, "Pozycja musi być obiektem"))
            continue

        for pole in POLA_WYMAGANE:
            if pole not in wino:
                bledy.append(_blad(i, pole, "Pole wymagane"))
        for pole in wino:
            if pole not in POLA_WYMAGANE + POLA_OPCJONALNE:
                bledy.append(_blad(i, pole, f"Nieznane pole: {pole}"))

        ident = wino.get("id", "")
        if not isinstance(ident, str) or not WZOR_ID.match(ident or ""):
            bledy.append(_blad(i, "id", "Dozwolone małe litery, cyfry i myślnik"))
        elif ident in widziane_id:
            bledy.append(_blad(i, "id", f"Identyfikator „{ident}” już występuje"))
        else:
            widziane_id.add(ident)

        for pole in ("nazwa", "opis"):
            if not str(wino.get(pole, "")).strip():
                bledy.append(_blad(i, pole, "Pole wymagane"))

        if kategorie and wino.get("kategoria") not in kategorie:
            bledy.append(_blad(i, "kategoria", "Nieznana kategoria"))
        if dostepne_odmiany and wino.get("odmiana_slug") not in dostepne_odmiany:
            bledy.append(_blad(i, "odmiana_slug", "Nie ma strony odmiany o tym adresie"))
        if dostepne_zdjecia and wino.get("zdjecie") not in dostepne_zdjecia:
            bledy.append(_blad(i, "zdjecie", "Nie ma takiego zdjęcia"))

        cena = wino.get("cena_brutto")
        if not isinstance(cena, (int, float)) or isinstance(cena, bool) or cena <= 0:
            bledy.append(_blad(i, "cena_brutto", "Cena musi być liczbą dodatnią"))
        elif round(float(cena), 2) != float(cena):
            bledy.append(_blad(i, "cena_brutto", "Najwyżej dwa miejsca po przecinku"))

        rabat = wino.get("rabat_procent")
        if not isinstance(rabat, (int, float)) or isinstance(rabat, bool) or not 0 <= rabat <= 99:
            bledy.append(_blad(i, "rabat_procent", "Rabat poza zakresem 0–99"))

        poj = wino.get("pojemnosc_ml")
        if not isinstance(poj, int) or isinstance(poj, bool) or poj <= 0:
            bledy.append(_blad(i, "pojemnosc_ml", "Pojemność musi być liczbą dodatnią"))

        if not isinstance(wino.get("dostepne"), bool):
            bledy.append(_blad(i, "dostepne", "Pole musi być prawdą albo fałszem"))

    return bledy


def zapisz(dane: dict) -> None:
    """Kopia poprzedniej wersji + zapis atomowy.

    Przerwanie w polowie nie moze zostawic uszkodzonego JSON-a, bo plik podmieniamy
    dopiero gotowy (`os.replace`).
    """
    CENNIK.parent.mkdir(parents=True, exist_ok=True)
    if CENNIK.exists():
        KOPIA.write_bytes(CENNIK.read_bytes())
        os.chmod(KOPIA, PRAWA_PLIKU)
    tresc = json.dumps(dane, ensure_ascii=False, indent=2) + "\n"
    uchwyt, tymczasowy = tempfile.mkstemp(dir=str(CENNIK.parent), suffix=".tmp")
    try:
        with os.fdopen(uchwyt, "w", encoding="utf-8") as plik:
            plik.write(tresc)
        # mkstemp tworzy plik z prawami 600, a os.replace je zachowuje. Bez tego cennik
        # po pierwszym zapisie stawal sie czytelny wylacznie dla wlasciciela procesu.
        os.chmod(tymczasowy, PRAWA_PLIKU)
        os.replace(tymczasowy, CENNIK)
    except BaseException:
        Path(tymczasowy).unlink(missing_ok=True)
        raise


def stan_poczatkowy() -> dict:
    """Dane, ktorych panel potrzebuje przy starcie."""
    return {
        "cennik": wczytaj(),
        "zdjecia": slugi_zdjec(),
        "odmiany": slugi_odmian(),
        "sciezka": str(CENNIK),
    }
