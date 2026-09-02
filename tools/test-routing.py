#!/usr/bin/env python3
"""Testy routingu wsgi.py bez instalowania Flaska.

Flask nie jest zainstalowany lokalnie (patrz AGENTS.md → Commands), a routing to jedyna
logika w tym pliku i akurat ta, ktora latwo zepsuc. Podstawiamy wiec atrape Flaska
i sprawdzamy same decyzje: ktory plik zostanie oddany i z jakim kodem.

Uruchomienie: python3 tools/test-routing.py
"""
import sys
import types
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent


# --- atrapa Flaska ----------------------------------------------------------
class _App:
    def __init__(self, *_, **__):
        pass

    def route(self, *_, **__):
        return lambda funkcja: funkcja


def _send_from_directory(katalog, sciezka):
    return f"PLIK:{sciezka}"


flask = types.ModuleType("flask")
flask.Flask = _App
flask.send_from_directory = _send_from_directory
sys.modules["flask"] = flask

sys.path.insert(0, str(PROJEKT))
import wsgi  # noqa: E402  (import po podstawieniu atrapy)


def wynik(sciezka: str) -> tuple[str, int]:
    """Zwraca (oddany_plik, kod_http) dla danego adresu."""
    odpowiedz = wsgi.serve(sciezka)
    if isinstance(odpowiedz, tuple):
        return odpowiedz[0], odpowiedz[1]
    return odpowiedz, 200


PRZYPADKI = [
    # adres,                          oczekiwany plik,               kod
    ("",                              "index.html",                  200),
    ("index.html",                    "index.html",                  200),
    ("wina/monarch.html",             "wina/monarch.html",           200),
    ("wina/soki.html",                "wina/soki.html",              200),
    ("data/wina.json",                "data/wina.json",              200),
    ("assets/js/produkty.js",         "assets/js/produkty.js",       200),
    ("sitemap.xml",                   "sitemap.xml",                 200),
    ("robots.txt",                    "robots.txt",                  200),
    # ladniejsze adresy bez rozszerzenia
    ("wina/monarch",                  "wina/monarch.html",           200),
    ("wina/monarch/",                 "wina/monarch.html",           200),
    # nieznane adresy: 404, a NIE strona glowna ze statusem 200
    ("wina/nie-ma-takiej-odmiany",    "404.html",                    404),
    ("wina/literowka.html",           "404.html",                    404),
    ("nie-ma-takiego-pliku.jpg",      "404.html",                    404),
    ("zupelnie/wymyslona/sciezka",    "404.html",                    404),
    # proby wyjscia poza katalog projektu
    ("../wsgi.py",                    "404.html",                    404),
    ("../../etc/passwd",              "404.html",                    404),
    # pliki, ktore NIE moga byc publiczne mimo ze leza w katalogu repozytorium
    ("wsgi.py",                       "404.html",                    404),
    ("AGENTS.md",                     "404.html",                    404),
    ("TODO.md",                       "404.html",                    404),
    ("CLAUDE.md",                     "404.html",                    404),
    ("tools/panel/serwer.py",         "404.html",                    404),
    ("tools/optimize-photos.py",      "404.html",                    404),
    (".git/config",                   "404.html",                    404),
    (".ai/GUARDRAILS.md",             "404.html",                    404),
    ("data/wina.json.bak",            "404.html",                    404),
    # a te musza dzialac dalej
    ("attached_assets/photos/winnica-panorama-01.jpg",
                                      "attached_assets/photos/winnica-panorama-01.jpg", 200),
    ("assets/css/custom.css",         "assets/css/custom.css",       200),
    ("filmy/README.md",               "filmy/README.md",             200),
    # panel: sam plik publiczny, ale katalogi tools/ juz nie
    ("tools/panel/panel.html",        "tools/panel/panel.html",      200),
    ("tools/panel/panel.css",         "tools/panel/panel.css",       200),
    ("tools/panel/panel.js",          "tools/panel/panel.js",        200),
    ("tools/panel/README.md",         "404.html",                    404),
    ("tools/panel",                   "404.html",                    404),
    ("tools",                         "404.html",                    404),
    ("404.html",                      "404.html",                    200),
]


def main() -> int:
    bledy = 0
    for sciezka, oczekiwany_plik, oczekiwany_kod in PRZYPADKI:
        plik, kod = wynik(sciezka)
        plik = plik.removeprefix("PLIK:")
        ok = plik == oczekiwany_plik and kod == oczekiwany_kod
        status = "OK  " if ok else "BLAD"
        print(f"{status}  /{sciezka:<32} → {plik} [{kod}]")
        if not ok:
            print(f"        oczekiwano: {oczekiwany_plik} [{oczekiwany_kod}]")
            bledy += 1

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
