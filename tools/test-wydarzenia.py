#!/usr/bin/env python3
"""Testy modulu wydarzen: sciezka robocza, zapis, walidacja i granice widocznosci.

Odpowiednik `test-cennik-sciezka.py` dla drugiego pliku danych. Dochodzi tu jeszcze
`aktywne()` — funkcja, ktora decyduje, czy wpis w ogole opusci serwer. Granice sprawdzamy
przez wstrzykniety `dzis`, zeby test nie zalezal od kalendarza w dniu uruchomienia.

Uruchomienie: python3 tools/test-wydarzenia.py
"""
import importlib
import json
import os
import shutil
import stat
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


def wpis(ident, od, do, tytul="Tytuł", tresc="Treść"):
    return {"id": ident, "tytul": tytul, "tresc": tresc, "data_od": od, "data_do": do}


def main() -> int:
    import wydarzenia

    # 1) domyslnie: plik z repozytorium ---------------------------------------
    os.environ.pop("WYDARZENIA_SCIEZKA", None)
    importlib.reload(wydarzenia)
    sprawdz("bez zmiennej: uzywa data/wydarzenia.json z repo",
            wydarzenia.WYDARZENIA == wydarzenia.WYDARZENIA_W_REPO)
    sprawdz("opis kopii w repo jest wzgledny",
            wydarzenia.opis_kopii() == "data/wydarzenia.json.bak")

    # 2) granice widocznosci --------------------------------------------------
    dane = {"wydarzenia": [
        wpis("trwajace", "2026-09-10", "2026-09-12"),
        wpis("jednodniowe", "2026-09-11", "2026-09-11"),
    ]}
    widoczne = lambda dzis: [w["id"] for w in wydarzenia.aktywne(dane, dzis)["wydarzenia"]]

    sprawdz("dzien przed poczatkiem: nic", widoczne("2026-09-09") == [])
    sprawdz("dzien poczatku wliczony", widoczne("2026-09-10") == ["trwajace"])
    sprawdz("srodek przedzialu", widoczne("2026-09-11") == ["trwajace", "jednodniowe"])
    sprawdz("dzien konca wliczony", widoczne("2026-09-12") == ["trwajace"])
    sprawdz("dzien po koncu: nic", widoczne("2026-09-13") == [])
    sprawdz("wpis bez dat nie przechodzi filtra",
            wydarzenia.aktywne({"wydarzenia": [{"id": "x"}]}, "2026-09-11")["wydarzenia"] == [])
    sprawdz("uszkodzona struktura zwraca pusta liste",
            wydarzenia.aktywne({"wydarzenia": "nie lista"}, "2026-09-11") == {"wydarzenia": []})
    sprawdz("dzis_w_winnicy ma format RRRR-MM-DD",
            len(wydarzenia.dzis_w_winnicy()) == 10 and wydarzenia.dzis_w_winnicy()[4] == "-")

    # 2b) data publikacji — zapowiedz przed terminem -------------------------
    zapowiedziane = {"wydarzenia": [
        dict(wpis("zapowiedz", "2026-10-01", "2026-10-05"), data_publikacji_od="2026-09-01"),
        wpis("bez-pola", "2026-10-01", "2026-10-05"),
    ]}
    widoczne2 = lambda dzis: [w["id"] for w in wydarzenia.aktywne(zapowiedziane, dzis)["wydarzenia"]]

    sprawdz("dzien przed publikacja: nic", widoczne2("2026-08-31") == [])
    sprawdz("dzien publikacji wliczony", widoczne2("2026-09-01") == ["zapowiedz"])
    sprawdz("miedzy publikacja a terminem widac tylko zapowiedziane",
            widoczne2("2026-09-15") == ["zapowiedz"])
    sprawdz("w terminie widac oba", widoczne2("2026-10-01") == ["zapowiedz", "bez-pola"])
    sprawdz("po data_do znika takze zapowiedziane", widoczne2("2026-10-06") == [])
    sprawdz("brak pola = zachowanie sprzed zmiany (start od data_od)",
            widoczne2("2026-09-15") == ["zapowiedz"] and widoczne2("2026-10-01") == ["zapowiedz", "bez-pola"])
    sprawdz("puste pole traktowane jak brak",
            [w["id"] for w in wydarzenia.aktywne(
                {"wydarzenia": [dict(wpis("x", "2026-10-01", "2026-10-05"), data_publikacji_od="")]},
                "2026-09-15")["wydarzenia"]] == [])
    sprawdz("poczatek_publikacji zwraca date publikacji, gdy jest",
            wydarzenia.poczatek_publikacji(
                dict(wpis("x", "2026-10-01", "2026-10-05"), data_publikacji_od="2026-09-01")) == "2026-09-01")
    sprawdz("poczatek_publikacji spada na data_od, gdy pola brak",
            wydarzenia.poczatek_publikacji(wpis("x", "2026-10-01", "2026-10-05")) == "2026-10-01")

    # 3) walidacja ------------------------------------------------------------
    sprawdz("poprawne dane bez bledow", wydarzenia.waliduj(dane) == [])
    sprawdz("wydarzenie jednodniowe jest poprawne",
            wydarzenia.waliduj({"wydarzenia": [wpis("a", "2026-09-11", "2026-09-11")]}) == [])

    def pola_bledow(dane_):
        return {(b["pozycja"], b["pole"]) for b in wydarzenia.waliduj(dane_)}

    sprawdz("data do wczesniejsza niz od",
            (0, "data_do") in pola_bledow({"wydarzenia": [wpis("a", "2026-10-05", "2026-09-20")]}))
    sprawdz("data nieistniejaca w kalendarzu (2026-02-30)",
            (0, "data_od") in pola_bledow({"wydarzenia": [wpis("a", "2026-02-30", "2026-03-01")]}))
    sprawdz("zly format daty",
            (0, "data_od") in pola_bledow({"wydarzenia": [wpis("a", "10.09.2026", "2026-09-11")]}))
    sprawdz("pusty tytul",
            (0, "tytul") in pola_bledow({"wydarzenia": [wpis("a", "2026-09-10", "2026-09-11", tytul="  ")]}))
    sprawdz("pusta tresc",
            (0, "tresc") in pola_bledow({"wydarzenia": [wpis("a", "2026-09-10", "2026-09-11", tresc="")]}))
    sprawdz("zbyt dlugi tytul",
            (0, "tytul") in pola_bledow(
                {"wydarzenia": [wpis("a", "2026-09-10", "2026-09-11", tytul="x" * 121)]}))
    sprawdz("zduplikowany identyfikator",
            (1, "id") in pola_bledow({"wydarzenia": [
                wpis("ten-sam", "2026-09-10", "2026-09-11"),
                wpis("ten-sam", "2026-09-12", "2026-09-13")]}))
    sprawdz("identyfikator z wielka litera odrzucony",
            (0, "id") in pola_bledow({"wydarzenia": [wpis("Zle-ID", "2026-09-10", "2026-09-11")]}))
    nadmiarowe = {"wydarzenia": [dict(wpis("a", "2026-09-10", "2026-09-11"), cena=10)]}
    sprawdz("nieznane pole odrzucone", (0, "cena") in pola_bledow(nadmiarowe))

    # pola opcjonalne: data publikacji
    sprawdz("data publikacji przed terminem jest poprawna",
            wydarzenia.waliduj({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), data_publikacji_od="2026-09-01")]}) == [])
    sprawdz("data publikacji pozniejsza niz data_do odrzucona",
            (0, "data_publikacji_od") in pola_bledow({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), data_publikacji_od="2026-11-01")]}))
    sprawdz("zly format daty publikacji odrzucony",
            (0, "data_publikacji_od") in pola_bledow({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), data_publikacji_od="01.09.2026")]}))
    sprawdz("pusta data publikacji nie jest bledem",
            wydarzenia.waliduj({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), data_publikacji_od="")]}) == [])

    # pola opcjonalne: zdjecie
    dostepne = sorted(p.stem for p in wydarzenia.PROJEKT_ZDJEC.glob("*.jpg")
                      if not p.stem.endswith("-sm"))
    sprawdz("biblioteka zdjec nie jest pusta", len(dostepne) > 0)
    if dostepne:
        sprawdz("istniejace zdjecie przechodzi",
                wydarzenia.waliduj({"wydarzenia": [
                    dict(wpis("a", "2026-10-01", "2026-10-05"), zdjecie=dostepne[0])]}) == [])
    sprawdz("nieistniejace zdjecie odrzucone",
            (0, "zdjecie") in pola_bledow({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), zdjecie="nie-ma-takiego-pliku")]}))
    sprawdz("proba wyjscia poza katalog zdjec odrzucona",
            (0, "zdjecie") in pola_bledow({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), zdjecie="../wsgi")]}))
    sprawdz("wariant -sm nie jest dozwolony jako slug",
            (0, "zdjecie") in pola_bledow({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"),
                     zdjecie=(dostepne[0] + "-sm") if dostepne else "cokolwiek-sm")]}))
    sprawdz("puste zdjecie nie jest bledem",
            wydarzenia.waliduj({"wydarzenia": [
                dict(wpis("a", "2026-10-01", "2026-10-05"), zdjecie="")]}) == [])
    sprawdz("brak listy wydarzen", pola_bledow({}) == {(None, "wydarzenia")})
    sprawdz("nie-obiekt odrzucony", wydarzenia.waliduj([]) == [
        {"pozycja": None, "pole": None, "komunikat": "Oczekiwano obiektu JSON"}])

    # 4) sciezka robocza poza projektem + zapis --------------------------------
    katalog = Path(tempfile.mkdtemp(prefix="wydarzenia-test-"))
    try:
        os.environ["WYDARZENIA_SCIEZKA"] = str(katalog / "dane" / "wydarzenia.json")
        importlib.reload(wydarzenia)
        sprawdz("ze zmienna: sciezka poza projektem",
                not wydarzenia.WYDARZENIA.is_relative_to(wydarzenia.PROJEKT))
        sprawdz("kopia .bak obok pliku roboczego",
                wydarzenia.KOPIA.parent == wydarzenia.WYDARZENIA.parent
                and wydarzenia.KOPIA.name.endswith(".json.bak"))

        wydarzenia.zapewnij_plik()
        sprawdz("zasiew tworzy plik roboczy z wersji w repo", wydarzenia.WYDARZENIA.is_file())
        sprawdz("zasiany plik ma poprawny JSON",
                isinstance(wydarzenia.wczytaj().get("wydarzenia"), list))

        wydarzenia.zapisz(dane)
        sprawdz("zapis utrwala dane", wydarzenia.wczytaj() == dane)
        prawa = stat.S_IMODE(wydarzenia.WYDARZENIA.stat().st_mode)
        sprawdz(f"prawa pliku 0o640 (jest {oct(prawa)})", prawa == wydarzenia.PRAWA_PLIKU)

        drugie = {"wydarzenia": [wpis("inne", "2026-11-01", "2026-11-02")]}
        wydarzenia.zapisz(drugie)
        sprawdz("kopia .bak trzyma poprzednia wersje",
                json.loads(wydarzenia.KOPIA.read_text(encoding="utf-8")) == dane)
        sprawdz("po drugim zapisie plik ma nowa wersje", wydarzenia.wczytaj() == drugie)
        sprawdz("po zapisie nie zostaja pliki tymczasowe",
                list(wydarzenia.WYDARZENIA.parent.glob("*.tmp")) == [])
        sprawdz("opis kopii poza projektem to pelna sciezka",
                wydarzenia.opis_kopii() == str(wydarzenia.KOPIA))

        stan = wydarzenia.stan_poczatkowy()
        sprawdz("stan_poczatkowy zwraca wszystkie wpisy, takze nieaktywne",
                [w["id"] for w in stan["wydarzenia"]] == ["inne"])
        sprawdz("stan_poczatkowy podaje sciezke pliku roboczego",
                stan["sciezka"] == str(wydarzenia.WYDARZENIA))

        # zasiew nie moze nadpisac pracy redakcyjnej
        wydarzenia.zapewnij_plik()
        sprawdz("zasiew nie nadpisuje istniejacego pliku", wydarzenia.wczytaj() == drugie)
    finally:
        shutil.rmtree(katalog, ignore_errors=True)
        os.environ.pop("WYDARZENIA_SCIEZKA", None)
        importlib.reload(wydarzenia)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
