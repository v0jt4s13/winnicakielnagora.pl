"""Wydarzenia winnicy — odczyt, walidacja, zapis i filtr widocznosci `data/wydarzenia.json`.

Blizniaczy modul do `cennik.py` i z tego samego powodu: obsluguje dwa wejscia panelu
  * `tools/panel/serwer.py` — panel uruchamiany lokalnie,
  * `wsgi.py` — panel na produkcji, za haslem,
wiec obie drogi walidują dane dokladnie tak samo. Modul nie zna HTTP.

Mieszka tu takze filtr widocznosci (`aktywne`). To nie jest wygoda, tylko wymog
`.ai/GUARDRAILS.md` → „Architectural boundaries" #3: `wsgi.py` poza panelem redakcyjnym
NIGDY nie dostaje logiki biznesowej. Publiczna trasa /data/wydarzenia.json ma tylko wolac
te funkcje i oddac wynik.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent

# Wersja startowa, wersjonowana w repozytorium. Na produkcji sluzy tylko do zasiania
# pliku roboczego przy pierwszym uruchomieniu.
WYDARZENIA_W_REPO = PROJEKT / "data" / "wydarzenia.json"

# Zywe wydarzenia. Na produkcji wskaz je POZA katalog wdrozenia (WYDARZENIA_SCIEZKA),
# zeby kolejny deploy nie skasowal wpisow zrobionych panelem — ten sam uklad co przy
# cenniku, patrz TODO #26.
WYDARZENIA = Path(os.environ.get("WYDARZENIA_SCIEZKA") or WYDARZENIA_W_REPO).expanduser()
KOPIA = WYDARZENIA.with_suffix(WYDARZENIA.suffix + ".bak")

SZKIELET: dict = {"wydarzenia": []}

# Wlasciciel i grupa moga czytac, reszta nie. Grupa to zwykle www-data.
PRAWA_PLIKU = 0o640

POLA_WYMAGANE = ("id", "tytul", "tresc", "data_od", "data_do")
WZOR_ID = re.compile(r"^[a-z0-9-]+$")
WZOR_DATY = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MAX_TYTUL = 120
MAX_TRESC = 2000


def zapewnij_plik() -> None:
    """Przy pierwszym uruchomieniu kopiuje wersje z repozytorium na sciezke robocza."""
    if WYDARZENIA.exists() or WYDARZENIA == WYDARZENIA_W_REPO:
        return
    WYDARZENIA.parent.mkdir(parents=True, exist_ok=True)
    if WYDARZENIA_W_REPO.exists():
        WYDARZENIA.write_bytes(WYDARZENIA_W_REPO.read_bytes())


def wczytaj() -> dict:
    """Zwraca wydarzenia. Gdy pliku nie ma — szkielet, ale go nie tworzy."""
    if not WYDARZENIA.exists():
        return {"wydarzenia": []}
    return json.loads(WYDARZENIA.read_text(encoding="utf-8"))


def dzis_w_winnicy() -> str:
    """Dzisiejsza data w strefie winnicy, jako 'YYYY-MM-DD'.

    Serwer moze stac w UTC, a przegladarka gdziekolwiek — o tym, czy wpis jest juz
    widoczny, decyduje kalendarz w Kielnarowej.
    """
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat()
    except Exception:
        # Brak bazy stref (tzdata) nie moze wywalic strony glownej.
        return date.today().isoformat()


def aktywne(dane: dict, dzis: str | None = None) -> dict:
    """Zawezenie do wpisow widocznych danego dnia: data_od <= dzis <= data_do.

    Granice sa domkniete z obu stron. Daty ISO porownujemy jako napisy — dla formatu
    YYYY-MM-DD porzadek leksykograficzny jest tozsamy z chronologicznym.

    `dzis` jest argumentem, a nie tylko odczytem zegara, zeby dalo sie sprawdzic granice
    przedzialu testem, bez czekania na kalendarz.
    """
    if dzis is None:
        dzis = dzis_w_winnicy()
    wpisy = dane.get("wydarzenia")
    if not isinstance(wpisy, list):
        return {"wydarzenia": []}
    return {"wydarzenia": [
        wpis for wpis in wpisy
        if isinstance(wpis, dict)
        and isinstance(wpis.get("data_od"), str)
        and isinstance(wpis.get("data_do"), str)
        and wpis["data_od"] <= dzis <= wpis["data_do"]
    ]}


def _blad(pozycja, pole, komunikat) -> dict:
    return {"pozycja": pozycja, "pole": pole, "komunikat": komunikat}


def _data_ok(wartosc) -> bool:
    """Format ORAZ istnienie w kalendarzu — sam wzorzec przepuscilby 2026-02-30."""
    if not isinstance(wartosc, str) or not WZOR_DATY.match(wartosc):
        return False
    try:
        date.fromisoformat(wartosc)
    except ValueError:
        return False
    return True


def waliduj(dane) -> list[dict]:
    """Lista bledow; pusta oznacza dane gotowe do zapisu.

    Serwer jest instancja rozstrzygajaca — przegladarce nie ufamy nawet lokalnie.
    """
    bledy: list[dict] = []
    if not isinstance(dane, dict):
        return [_blad(None, None, "Oczekiwano obiektu JSON")]

    wpisy = dane.get("wydarzenia")
    if not isinstance(wpisy, list):
        return bledy + [_blad(None, "wydarzenia", "Brak listy wydarzeń")]

    widziane_id: set[str] = set()

    for i, wpis in enumerate(wpisy):
        if not isinstance(wpis, dict):
            bledy.append(_blad(i, None, "Wydarzenie musi być obiektem"))
            continue

        for pole in POLA_WYMAGANE:
            if pole not in wpis:
                bledy.append(_blad(i, pole, "Pole wymagane"))
        for pole in wpis:
            if pole not in POLA_WYMAGANE:
                bledy.append(_blad(i, pole, f"Nieznane pole: {pole}"))

        ident = wpis.get("id", "")
        if not isinstance(ident, str) or not WZOR_ID.match(ident or ""):
            bledy.append(_blad(i, "id", "Dozwolone małe litery, cyfry i myślnik"))
        elif ident in widziane_id:
            bledy.append(_blad(i, "id", f"Identyfikator „{ident}” już występuje"))
        else:
            widziane_id.add(ident)

        tytul = wpis.get("tytul")
        if not isinstance(tytul, str) or not tytul.strip():
            bledy.append(_blad(i, "tytul", "Pole wymagane"))
        elif len(tytul.strip()) > MAX_TYTUL:
            bledy.append(_blad(i, "tytul", f"Najwyżej {MAX_TYTUL} znaków"))

        tresc = wpis.get("tresc")
        if not isinstance(tresc, str) or not tresc.strip():
            bledy.append(_blad(i, "tresc", "Pole wymagane"))
        elif len(tresc.strip()) > MAX_TRESC:
            bledy.append(_blad(i, "tresc", f"Najwyżej {MAX_TRESC} znaków"))

        for pole in ("data_od", "data_do"):
            if not _data_ok(wpis.get(pole)):
                bledy.append(_blad(i, pole, "Wymagana poprawna data w formacie RRRR-MM-DD"))

        if _data_ok(wpis.get("data_od")) and _data_ok(wpis.get("data_do")):
            if wpis["data_do"] < wpis["data_od"]:
                bledy.append(_blad(
                    i, "data_do", "„data do” nie może być wcześniejsza niż „data od”"))

    return bledy


def zapisz(dane: dict) -> None:
    """Kopia poprzedniej wersji + zapis atomowy.

    Przerwanie w polowie nie moze zostawic uszkodzonego JSON-a, bo plik podmieniamy
    dopiero gotowy (`os.replace`).
    """
    WYDARZENIA.parent.mkdir(parents=True, exist_ok=True)
    if WYDARZENIA.exists():
        KOPIA.write_bytes(WYDARZENIA.read_bytes())
        os.chmod(KOPIA, PRAWA_PLIKU)
    tresc = json.dumps(dane, ensure_ascii=False, indent=2) + "\n"
    uchwyt, tymczasowy = tempfile.mkstemp(dir=str(WYDARZENIA.parent), suffix=".tmp")
    try:
        with os.fdopen(uchwyt, "w", encoding="utf-8") as plik:
            plik.write(tresc)
        # mkstemp tworzy plik z prawami 600, a os.replace je zachowuje — bez tego plik
        # po pierwszym zapisie stawalby sie czytelny wylacznie dla wlasciciela procesu.
        os.chmod(tymczasowy, PRAWA_PLIKU)
        os.replace(tymczasowy, WYDARZENIA)
    except BaseException:
        Path(tymczasowy).unlink(missing_ok=True)
        raise


def opis_kopii() -> str:
    """Sciezka kopii zapasowej do pokazania w interfejsie."""
    try:
        return str(KOPIA.relative_to(PROJEKT))
    except ValueError:
        return str(KOPIA)


def stan_poczatkowy() -> dict:
    """Dane, ktorych panel potrzebuje przy starcie — wszystkie wpisy, takze nieaktywne."""
    return {
        "wydarzenia": wczytaj().get("wydarzenia", []),
        "sciezka": str(WYDARZENIA),
    }
