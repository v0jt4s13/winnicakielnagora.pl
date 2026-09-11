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
    sprawdz("opis kopii w repo jest wzgledny", cennik.opis_kopii() == "data/wina.json.bak")
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
        sprawdz("cennik ma prawa 640, nie 600 po mkstemp",
                oct(cennik.CENNIK.stat().st_mode)[-3:] == "640")
        sprawdz("kopia zapasowa ma te same prawa",
                oct(cennik.KOPIA.stat().st_mode)[-3:] == "640")

        # 5) opis kopii nie moze sie wysypac, gdy cennik jest poza projektem.
        #    Wczesniej KOPIA.relative_to(PROJEKT) rzucalo ValueError JUZ PO udanym
        #    zapisie, wiec dane sie zapisywaly, a panel dostawal 500.
        try:
            opis = cennik.opis_kopii()
            sprawdz("opis kopii nie rzuca wyjatku poza projektem", True)
            sprawdz("opis kopii to pelna sciezka", opis == str(cennik.KOPIA))
        except Exception as blad:
            sprawdz(f"opis kopii nie rzuca wyjatku poza projektem ({blad})", False)

        # 6) ponowny zasiew nie nadpisuje istniejacego pliku
        cennik.zapewnij_plik()
        sprawdz("zasiew nie nadpisuje istniejacego cennika",
                json.loads(cennik.CENNIK.read_text(encoding="utf-8"))["wina"] == [])

        # 7) zapisz_bezpiecznie — wykrywanie utraconego zapisu (KonfliktZapisu).
        #    Scenariusz z wypadku: "edytor B" wczytal plik ZANIM "edytor A" zapisal
        #    swoja zmiane, wiec B probuje zapisac na podstawie juz nieaktualnej wersji.
        wersja_przed = cennik.wersja_pliku()
        stan_widziany_przez_b = cennik.wczytaj()  # migawka SPRZED zapisu A

        dane_a = cennik.wczytaj()
        dane_a["wina"] = [{"id": "test-a", "nazwa": "Test A"}]
        wersja_po_a = cennik.zapisz_bezpiecznie(dane_a, wersja_przed)
        sprawdz("zapisz_bezpiecznie ze świeżą wersją: przechodzi i zwraca nowy hash",
                wersja_po_a != wersja_przed and wersja_po_a == cennik.wersja_pliku())

        dane_b = cennik.wczytaj()
        dane_b["wina"] = stan_widziany_przez_b["wina"] + [{"id": "test-b", "nazwa": "Test B"}]
        try:
            cennik.zapisz_bezpiecznie(dane_b, wersja_przed, bazowe_dane=stan_widziany_przez_b)
            sprawdz("zapisz_bezpiecznie z nieaktualną wersją rzuca KonfliktZapisu", False)
        except cennik.KonfliktZapisu as konflikt:
            sprawdz("KonfliktZapisu niesie aktualną (nie odrzuconą) wersję",
                    konflikt.aktualna_wersja == wersja_po_a)
            sprawdz("KonfliktZapisu wskazuje w różnicach zmianę, której B nie widział",
                    any("Test A" in r for r in konflikt.roznice))
        sprawdz("odrzucony zapis B nie dotknął pliku (zostaje wersja po A)",
                cennik.wersja_pliku() == wersja_po_a)
        sprawdz("odrzucony zapis B nie dotknął pliku (zawartość też nietknięta)",
                cennik.wczytaj()["wina"] == dane_a["wina"])
    finally:
        shutil.rmtree(katalog, ignore_errors=True)
        os.environ.pop("CENNIK_SCIEZKA", None)
        importlib.reload(cennik)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
