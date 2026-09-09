"""Bezpieczne operacje na obrazach w katalogu ``attached_assets``.

Moduł jest współdzielony przez lokalny panel i panel produkcyjny. Nie udostępnia
plików samodzielnie - zwraca dane i wykonuje operacje po wcześniejszym sprawdzeniu,
że każda ścieżka pozostaje wewnątrz katalogu zasobów.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent
ZASOBY = PROJEKT / "attached_assets"
ROZSZERZENIA = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ROZMIARY_WARIANTOW = {"sm": 600, "thumb": 300}
SUFIKS_WARIANTU = re.compile(r"-(?:sm|thumb)$", re.IGNORECASE)
MAKS_PLIKOW = 200


def _wzgledna(wartosc: object, *, katalog: bool = False) -> Path:
    if not isinstance(wartosc, str) or "\x00" in wartosc or "\\" in wartosc:
        raise ValueError("Ścieżka ma nieprawidłowy format")
    if not wartosc and katalog:
        return ZASOBY.resolve()
    if not wartosc or Path(wartosc).is_absolute():
        raise ValueError("Ścieżka musi być względna względem attached_assets")

    surowa = Path(wartosc)
    if any(czesc in ("", ".", "..") for czesc in surowa.parts):
        raise ValueError("Ścieżka nie może zawierać ., .. ani pustych składników")
    kandydat = (ZASOBY / surowa).resolve()
    if not kandydat.is_relative_to(ZASOBY.resolve()):
        raise ValueError("Ścieżka wychodzi poza attached_assets")
    return kandydat


def _relatywna(sciezka: Path) -> str:
    return sciezka.resolve().relative_to(ZASOBY.resolve()).as_posix()


def _plik(wartosc: object) -> Path:
    kandydat = _wzgledna(wartosc)
    if not kandydat.is_file() or kandydat.suffix.lower() not in ROZSZERZENIA:
        raise ValueError("Wskazany plik nie jest obrazem w attached_assets")
    return kandydat


def _katalog(wartosc: object) -> Path:
    kandydat = _wzgledna(wartosc, katalog=True)
    if not kandydat.is_dir():
        raise ValueError("Katalog docelowy nie istnieje")
    return kandydat


def _wymiary(plik: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(plik) as obraz:
            return obraz.width, obraz.height
    except (ImportError, OSError):
        return None, None


def stan() -> dict:
    """Zwraca katalogi i obrazy, ale nigdy pliki niegraficzne."""
    if not ZASOBY.is_dir():
        return {"katalogi": [], "pliki": []}

    katalogi = {""}
    pliki = []
    zasoby = ZASOBY.resolve()
    for sciezka in ZASOBY.rglob("*"):
        try:
            rozwiazana = sciezka.resolve()
            if not rozwiazana.is_relative_to(zasoby):
                continue
        except OSError:
            continue
        if sciezka.is_dir():
            katalogi.add(_relatywna(sciezka))
        elif sciezka.is_file() and sciezka.suffix.lower() in ROZSZERZENIA:
            rel = _relatywna(sciezka)
            katalog = sciezka.parent.resolve().relative_to(zasoby).as_posix()
            if katalog == ".":
                katalog = ""
            szerokosc, wysokosc = _wymiary(sciezka)
            pliki.append({
                "sciezka": rel,
                "katalog": katalog,
                "nazwa": sciezka.name,
                "rozmiar": sciezka.stat().st_size,
                "szerokosc": szerokosc,
                "wysokosc": wysokosc,
            })

    return {
        "katalogi": sorted(katalogi, key=lambda wpis: (wpis != "", wpis.lower())),
        "pliki": sorted(pliki, key=lambda wpis: (wpis["katalog"].lower(), wpis["nazwa"].lower())),
    }


def przenies(pliki: object, katalog: object) -> int:
    """Przenosi obrazy do istniejącego katalogu bez nadpisywania celu."""
    if not isinstance(pliki, list) or not pliki or len(pliki) > MAKS_PLIKOW:
        raise ValueError(f"Wybierz od 1 do {MAKS_PLIKOW} obrazów")
    cel = _katalog(katalog)
    zrodla = [_plik(sciezka) for sciezka in pliki]
    cele = [cel / zrodlo.name for zrodlo in zrodla]
    if len({str(sciezka) for sciezka in zrodla}) != len(zrodla):
        raise ValueError("Ten sam obraz został wybrany więcej niż raz")
    if any(zrodlo.parent == cel for zrodlo in zrodla):
        raise ValueError("Co najmniej jeden obraz już jest w tym katalogu")
    if any(kandydat.exists() for kandydat in cele):
        raise ValueError("W katalogu docelowym istnieje już plik o tej nazwie")
    if len({str(kandydat) for kandydat in cele}) != len(cele):
        raise ValueError("Wybrane pliki mają powtarzające się nazwy")

    for zrodlo, kandydat in zip(zrodla, cele):
        zrodlo.rename(kandydat)
    return len(zrodla)


def _zapisz_wariant(obraz, cel: Path, rozszerzenie: str) -> None:
    fd, tymczasowy = tempfile.mkstemp(dir=cel.parent, prefix=f".{cel.stem}.", suffix=cel.suffix)
    os.close(fd)
    tymczasowy_path = Path(tymczasowy)
    try:
        if rozszerzenie in {".jpg", ".jpeg"}:
            obraz = obraz.convert("RGB")
            obraz.save(tymczasowy_path, "JPEG", quality=80, optimize=True, progressive=True)
        else:
            formaty = {".png": "PNG", ".webp": "WEBP", ".gif": "GIF"}
            obraz.save(tymczasowy_path, formaty[rozszerzenie], optimize=True)
        os.chmod(tymczasowy_path, 0o644)
        # Twarde dowiązanie tymczasowego pliku nie nadpisuje celu w razie wyścigu.
        os.link(tymczasowy_path, cel)
    finally:
        tymczasowy_path.unlink(missing_ok=True)


def utworz_warianty(pliki: object, warianty: object) -> dict:
    """Tworzy warianty w tych samych katalogach i pomija istniejące pliki."""
    if not isinstance(pliki, list) or not pliki or len(pliki) > MAKS_PLIKOW:
        raise ValueError(f"Wybierz od 1 do {MAKS_PLIKOW} obrazów")
    if not isinstance(warianty, list) or not warianty or any(w not in ROZMIARY_WARIANTOW for w in warianty):
        raise ValueError("Wybierz wariant -sm albo -thumb")

    try:
        from PIL import Image, ImageOps
    except ImportError as blad:
        raise RuntimeError("Tworzenie wariantów wymaga zainstalowanej biblioteki Pillow") from blad

    zrodla = [_plik(sciezka) for sciezka in pliki]
    utworzone = []
    istniejace = []
    widziane = set()
    for zrodlo in zrodla:
        podstawa = SUFIKS_WARIANTU.sub("", zrodlo.stem)
        for wariant in dict.fromkeys(warianty):
            cel = zrodlo.with_name(f"{podstawa}-{wariant}{zrodlo.suffix.lower()}")
            if cel in widziane or cel == zrodlo or cel.exists():
                istniejace.append(_relatywna(cel))
                continue
            widziane.add(cel)
            with Image.open(zrodlo) as otwarte:
                przeksztalcone = ImageOps.exif_transpose(otwarte).copy()
            przeksztalcone.thumbnail((ROZMIARY_WARIANTOW[wariant], ROZMIARY_WARIANTOW[wariant]), Image.LANCZOS)
            try:
                _zapisz_wariant(przeksztalcone, cel, zrodlo.suffix.lower())
            finally:
                przeksztalcone.close()
            utworzone.append(_relatywna(cel))

    return {"utworzono": len(utworzone), "pominieto": len(istniejace),
            "pliki": utworzone, "istniejace": istniejace}
