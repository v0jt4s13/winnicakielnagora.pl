#!/usr/bin/env python3
"""Testy operacji galerii na tymczasowym katalogu zasobów."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

from PIL import Image
import galeria


def sprawdz(opis: str, warunek: bool) -> None:
    if not warunek:
        raise AssertionError(opis)
    print(f"OK    {opis}")


def main() -> int:
    poprzednie_zasoby = galeria.ZASOBY
    with TemporaryDirectory() as tymczasowy:
        zasoby = Path(tymczasowy) / "attached_assets"
        (zasoby / "photos").mkdir(parents=True)
        (zasoby / "butelki").mkdir()
        Image.new("RGB", (1200, 800), "white").save(zasoby / "photos" / "wino.jpg")
        galeria.ZASOBY = zasoby
        try:
            stan = galeria.stan()
            sprawdz("listuje katalog główny i podkatalogi", stan["katalogi"] == ["", "butelki", "photos"])
            sprawdz("listuje tylko obrazy", [p["sciezka"] for p in stan["pliki"]] == ["photos/wino.jpg"])

            sprawdz("przenosi obraz", galeria.przenies(["photos/wino.jpg"], "butelki") == 1)
            sprawdz("obraz jest w katalogu docelowym", (zasoby / "butelki" / "wino.jpg").is_file())

            wynik = galeria.utworz_warianty(["butelki/wino.jpg"], ["sm", "thumb"])
            sprawdz("tworzy dwa warianty", wynik["utworzono"] == 2)
            with Image.open(zasoby / "butelki" / "wino-sm.jpg") as obraz:
                sprawdz("-sm ma dłuższy bok 600 px", max(obraz.size) == 600)
            with Image.open(zasoby / "butelki" / "wino-thumb.jpg") as obraz:
                sprawdz("-thumb ma dłuższy bok 300 px", max(obraz.size) == 300)

            wynik = galeria.utworz_warianty(["butelki/wino.jpg"], ["sm"])
            sprawdz("nie nadpisuje istniejącego wariantu", wynik["pominieto"] == 1)

            try:
                galeria.przenies(["../poza.jpg"], "")
            except ValueError:
                sprawdz("blokuje wyjście poza attached_assets", True)
            else:
                sprawdz("blokuje wyjście poza attached_assets", False)
        finally:
            galeria.ZASOBY = poprzednie_zasoby

    print("\nWSZYSTKIE TESTY PRZESZŁY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
