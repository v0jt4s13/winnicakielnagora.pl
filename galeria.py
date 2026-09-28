"""Bezpieczne operacje na obrazach w katalogu ``attached_assets``.

Moduł jest współdzielony przez lokalny panel i panel produkcyjny. Nie udostępnia
plików samodzielnie - zwraca dane i wykonuje operacje po wcześniejszym sprawdzeniu,
że każda ścieżka pozostaje wewnątrz katalogu zasobów.
"""
from __future__ import annotations

import errno
import os
import re
import shutil
import tempfile
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent
ZASOBY = PROJEKT / "attached_assets"
# Zdjecia wgrane z panelu (SPEC-009). Na produkcji to dowiazanie symboliczne do katalogu
# poza wdrozeniem (dane/uploads), wiec po resolve() lezy POZA ZASOBY — dlatego jest
# osobnym dozwolonym korzeniem, a sciezki wzgledne liczymy leksykalnie, nie z resolve().
KATALOG_UPLOADS = "uploads"
ROZSZERZENIA = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ROZMIARY_WARIANTOW = {"sm": 600, "thumb": 300}
SUFIKS_WARIANTU = re.compile(r"-(?:sm|thumb)$", re.IGNORECASE)
MAKS_PLIKOW = 200


def uploads() -> Path:
    """Katalog wgrywania liczony od biezacego ZASOBY (testy podmieniaja ZASOBY)."""
    return ZASOBY / KATALOG_UPLOADS


def _korzenie() -> tuple[Path, ...]:
    """Katalogi, w ktorych po rozwiazaniu dowiazan moze lezec plik galerii."""
    return (ZASOBY.resolve(), uploads().resolve())


def _w_korzeniach(sciezka: Path) -> bool:
    rozwiazana = sciezka.resolve()
    return any(rozwiazana.is_relative_to(korzen) for korzen in _korzenie())


def _wzgledna(wartosc: object, *, katalog: bool = False) -> Path:
    """Sciezka pod ZASOBY po walidacji; zwraca sciezke LEKSYKALNA (bez resolve()).

    Operacje na pliku ida za dowiazaniem same, a leksykalna postac pozwala policzyc
    wzgledna sciezke "uploads/x.jpg" takze wtedy, gdy uploads prowadzi poza ZASOBY.
    """
    if not isinstance(wartosc, str) or "\x00" in wartosc or "\\" in wartosc:
        raise ValueError("Ścieżka ma nieprawidłowy format")
    if not wartosc and katalog:
        return ZASOBY
    if not wartosc or Path(wartosc).is_absolute():
        raise ValueError("Ścieżka musi być względna względem attached_assets")

    surowa = Path(wartosc)
    if any(czesc in ("", ".", "..") for czesc in surowa.parts):
        raise ValueError("Ścieżka nie może zawierać ., .. ani pustych składników")
    kandydat = ZASOBY / surowa
    if not _w_korzeniach(kandydat):
        raise ValueError("Ścieżka wychodzi poza attached_assets")
    return kandydat


def _relatywna(sciezka: Path) -> str:
    return sciezka.relative_to(ZASOBY).as_posix()


def w_zasobach(wartosc: object) -> Path | None:
    """Istniejacy obraz pod attached_assets/ (lub uploads/) albo None.

    Jedyne sprawdzenie "czy ta sciezka to nasz obraz" dla galerii, cennika (zdjecie_sklep)
    i wydarzen (zdjecia) — wszystkie trzy musza tak samo przepuszczac dowiazane uploads/.
    """
    try:
        return _plik(wartosc)
    except ValueError:
        return None


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
    # rglob (Python 3.11) nie wchodzi do katalogow-dowiazan, wiec dowiazane uploads/
    # przechodzimy osobno. Gdy uploads jest zwyklym katalogiem, obejmuje go juz pierwszy rglob.
    kandydaci = list(ZASOBY.rglob("*"))
    if uploads().is_symlink() and uploads().is_dir():
        kandydaci += list(uploads().rglob("*"))
    for sciezka in kandydaci:
        try:
            if not _w_korzeniach(sciezka):
                continue
        except OSError:
            continue
        if sciezka.is_dir():
            katalogi.add(_relatywna(sciezka))
        elif sciezka.is_file() and sciezka.suffix.lower() in ROZSZERZENIA:
            rel = _relatywna(sciezka)
            katalog = _relatywna(sciezka.parent) if sciezka.parent != ZASOBY else ""
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
        try:
            zrodlo.rename(kandydat)
        except OSError as blad:
            # uploads/ na produkcji moze lezec na innym systemie plikow niz attached_assets
            # (dowiazanie do dane/) — rename() nie przenosi miedzy nimi.
            if blad.errno != errno.EXDEV:
                raise
            shutil.copy2(zrodlo, kandydat)
            zrodlo.unlink()
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


# --- wgrywanie i usuwanie (SPEC-009) ---------------------------------------------------

MAX_WGRYWANIE = 15 * 1024 * 1024
# Jawny limit zamiast domyslnego MAX_IMAGE_PIXELS Pillow, ktory miedzy 1x a 2x tylko ostrzega.
MAKS_PIKSELI = 50_000_000
MAKS_BOK = 2000
FORMATY_WGRYWANIA = {"JPEG", "PNG", "WEBP"}
_ZNAKI_PL = str.maketrans("ąćęłńóśźż", "acelnoszz")


class PlikUzywany(ValueError):
    """Usuwanie odrzucone: co najmniej jeden plik jest uzywany w danych strony."""

    def __init__(self, uzycia: dict[str, list[str]]):
        self.uzycia = uzycia
        super().__init__("Nie usunięto nic — część plików jest używana na stronie")


def slug_nazwy(nazwa: object) -> str:
    """Nazwa pliku z przegladarki -> bezpieczny slug bez rozszerzenia i bez katalogow."""
    surowa = str(nazwa or "").replace("\\", "/").split("/")[-1]
    rdzen = surowa.rsplit(".", 1)[0] if "." in surowa else surowa
    slug = re.sub(r"[^a-z0-9]+", "-", rdzen.lower().translate(_ZNAKI_PL)).strip("-")[:80].strip("-")
    # Koncowka -sm/-thumb oznacza w galerii wariant miniatury — nowy plik nie moze jej udawac.
    slug = SUFIKS_WARIANTU.sub("", slug)
    return slug or "zdjecie"


def wgraj(nazwa: object, dane: bytes) -> dict:
    """Dekoduje obraz, zmniejsza, usuwa metadane i zapisuje w uploads/ bez nadpisywania.

    Typ ustala dekoder, nie rozszerzenie; na dysk trafia wylacznie ponownie zakodowany obraz.
    """
    if not isinstance(dane, (bytes, bytearray)) or not dane:
        raise ValueError("Pusty plik")
    if len(dane) > MAX_WGRYWANIE:
        raise ValueError(f"Plik jest większy niż {MAX_WGRYWANIE // (1024 * 1024)} MB")
    try:
        import io

        from PIL import Image, ImageOps, UnidentifiedImageError
    except ImportError as blad:
        raise RuntimeError("Wgrywanie wymaga biblioteki Pillow na serwerze") from blad

    try:
        with Image.open(io.BytesIO(dane)) as otwarte:
            if otwarte.format not in FORMATY_WGRYWANIA:
                raise ValueError("To nie jest obraz JPG, PNG ani WebP")
            if otwarte.width * otwarte.height > MAKS_PIKSELI:
                raise ValueError("Obraz ma zbyt dużą rozdzielczość (ponad 50 Mpx)")
            icc = otwarte.info.get("icc_profile")
            obraz = ImageOps.exif_transpose(otwarte)
            obraz.load()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as blad:
        raise ValueError("To nie jest obraz JPG, PNG ani WebP") from blad

    przezroczysty = obraz.mode in ("RGBA", "LA", "PA") or (
        obraz.mode == "P" and "transparency" in obraz.info)
    obraz.thumbnail((MAKS_BOK, MAKS_BOK), Image.LANCZOS)
    szerokosc, wysokosc = obraz.width, obraz.height
    rozszerzenie = ".webp" if przezroczysty else ".jpg"

    katalog = uploads()
    try:
        katalog.mkdir(parents=True, exist_ok=True)
    except OSError as blad:
        raise RuntimeError(f"Katalog {katalog} nie istnieje i nie da się go utworzyć: {blad}") from blad
    if not _w_korzeniach(katalog):
        raise RuntimeError("Katalog uploads wskazuje poza dozwolone miejsca")

    fd, tymczasowy = tempfile.mkstemp(dir=katalog, prefix=".wgrywanie.", suffix=rozszerzenie)
    os.close(fd)
    tymczasowy_path = Path(tymczasowy)
    try:
        # Bez exif= : GPS, model aparatu i data znikaja. Profil ICC zostaje (kolory).
        dodatkowe = {"icc_profile": icc} if icc else {}
        if przezroczysty:
            obraz.convert("RGBA").save(tymczasowy_path, "WEBP", quality=85, **dodatkowe)
        else:
            obraz.convert("RGB").save(tymczasowy_path, "JPEG", quality=85, optimize=True,
                                      progressive=True, **dodatkowe)
        os.chmod(tymczasowy_path, 0o644)
        slug = slug_nazwy(nazwa)
        for numer in range(1, 1000):
            cel = katalog / f"{slug}{'' if numer == 1 else f'-{numer}'}{rozszerzenie}"
            try:
                # Twarde dowiazanie nie nadpisuje istniejacego pliku, takze przy wyscigu.
                os.link(tymczasowy_path, cel)
                break
            except FileExistsError:
                continue
        else:
            raise RuntimeError("Nie udało się dobrać wolnej nazwy pliku")
    finally:
        tymczasowy_path.unlink(missing_ok=True)
        obraz.close()

    return {"sciezka": _relatywna(cel), "szerokosc": szerokosc, "wysokosc": wysokosc,
            "rozmiar": cel.stat().st_size}


def uzycia_zdjec() -> dict[str, list[str]]:
    """Sciezka wzgledna obrazu -> gdzie jest uzywany (cennik: zdjecie_sklep, wydarzenia: zdjecia).

    Import wewnatrz funkcji: cennik i wydarzenia same importuja galeria (w_zasobach).
    Pola `zdjecie` (slug) wskazuja wylacznie photos/<slug>.jpg, a galeria "O nas" trzyma
    kopie w assets/, wiec zadne z nich nie moze dotyczyc uploads/.
    """
    import cennik
    import wydarzenia

    uzycia: dict[str, list[str]] = {}
    for wino in cennik.wczytaj().get("wina", []):
        sciezka = cennik.sciezka_zdjecia_sklep(wino.get("zdjecie_sklep"))
        if sciezka is not None:
            uzycia.setdefault(_relatywna(sciezka), []).append(
                f"cennik: {wino.get('nazwa', '?')} ({wino.get('id', '?')})")
    for wpis in wydarzenia.wczytaj().get("wydarzenia", []):
        for zdjecie in wpis.get("zdjecia") or []:
            sciezka = w_zasobach(zdjecie)
            if sciezka is not None:
                uzycia.setdefault(_relatywna(sciezka), []).append(
                    f"wydarzenie: {wpis.get('tytul', '?')}")
    return uzycia


def usun(pliki: object, uzycia: dict[str, list[str]]) -> int:
    """Usuwa obrazy z uploads/ — wszystko albo nic. Plik uzywany blokuje cala operacje."""
    if not isinstance(pliki, list) or not pliki or len(pliki) > MAKS_PLIKOW:
        raise ValueError(f"Wybierz od 1 do {MAKS_PLIKOW} obrazów")
    korzen = uploads().resolve()
    cele = []
    for wartosc in pliki:
        sciezka = _plik(wartosc)
        wzgledna = _relatywna(sciezka)
        if not wzgledna.startswith(f"{KATALOG_UPLOADS}/") or not sciezka.resolve().is_relative_to(korzen):
            raise ValueError(f"Z panelu można usuwać tylko pliki z {KATALOG_UPLOADS}/: {wzgledna}")
        cele.append((wzgledna, sciezka))
    if len({wzgledna for wzgledna, _ in cele}) != len(cele):
        raise ValueError("Ten sam obraz został wybrany więcej niż raz")
    zajete = {wzgledna: uzycia[wzgledna] for wzgledna, _ in cele if uzycia.get(wzgledna)}
    if zajete:
        raise PlikUzywany(zajete)
    for _, sciezka in cele:
        sciezka.unlink()
    return len(cele)
