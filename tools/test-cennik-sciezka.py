#!/usr/bin/env python3
"""Testy sciezki zywego cennika (CENNIK_SCIEZKA).

Wdrozenie pomija katalog data/, wiec zywy cennik musi zyc poza katalogiem aplikacji.
Ten test sprawdza, ze konfiguracja dziala i ze plik zasiewa sie z wersji w repozytorium.

Uruchomienie: python3 tools/test-cennik-sciezka.py
"""
import importlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

bledy = 0


def sprawdz(opis, warunek):
    global bledy
    print(f"{'OK  ' if warunek else 'BLAD'}  {opis}")
    if not warunek:
        bledy += 1


def main() -> int:
    import cennik

    # 1) domyslnie: plik z repozytorium
    os.environ.pop("CENNIK_SCIEZKA", None)
    importlib.reload(cennik)
    sprawdz("bez zmiennej: uzywa data/wina.json z repo", cennik.CENNIK == cennik.CENNIK_W_REPO)
    w_repo = len(cennik.wczytaj().get("wina", []))

    # 2) ze zmienna: plik poza katalogiem projektu
    katalog = Path(tempfile.mkdtemp(prefix="cennik-test-"))
    try:
        os.environ["CENNIK_SCIEZKA"] = str(katalog / "dane" / "wina.json")
        importlib.reload(cennik)
        sprawdz("ze zmienna: sciezka poza projektem",
                not cennik.CENNIK.is_relative_to(cennik.PROJEKT))
        sprawdz("kopia .bak obok pliku roboczego",
                cennik.KOPIA.parent == cennik.CENNIK.parent
                and cennik.KOPIA.name.endswith(".json.bak"))

        # 3) zasiew z repozytorium przy pierwszym uruchomieniu
        sprawdz("przed zasiewem pliku nie ma", not cennik.CENNIK.exists())
        cennik.zapewnij_plik()
        sprawdz("po zasiewie plik istnieje", cennik.CENNIK.exists())
        sprawdz("zasiana ta sama liczba pozycji", len(cennik.wczytaj()["wina"]) == w_repo)

        # 4) zapis idzie na sciezke robocza, repo zostaje nietkniete
        przed = cennik.CENNIK_W_REPO.read_bytes()
        dane = cennik.wczytaj()
        dane["wina"] = []
        cennik.zapisz(dane)
        sprawdz("zapis nie tyka pliku w repozytorium",
                cennik.CENNIK_W_REPO.read_bytes() == przed)
        sprawdz("zapis trafil na sciezke robocza",
                json.loads(cennik.CENNIK.read_text(encoding="utf-8"))["wina"] == [])
        sprawdz("powstala kopia zapasowa", cennik.KOPIA.exists())

        # 5) ponowny zasiew nie nadpisuje istniejacego pliku
        cennik.zapewnij_plik()
        sprawdz("zasiew nie nadpisuje istniejacego cennika",
                json.loads(cennik.CENNIK.read_text(encoding="utf-8"))["wina"] == [])
    finally:
        shutil.rmtree(katalog, ignore_errors=True)
        os.environ.pop("CENNIK_SCIEZKA", None)
        importlib.reload(cennik)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
