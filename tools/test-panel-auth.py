#!/usr/bin/env python3
"""Testy uwierzytelniania panelu na produkcji, bez instalowania Flaska.

Panel na produkcji zapisuje pliki, wiec jego zabezpieczenia musza byc sprawdzalne.
Flask nie jest zainstalowany lokalnie (AGENTS.md → Commands), podstawiamy wiec atrape
i wolamy funkcje wsgi.py wprost.

Uruchomienie: python3 tools/test-panel-auth.py
"""
import json
import os
import secrets
import sys
import types
from hashlib import pbkdf2_hmac
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent


class _App:
    def __init__(self, *a, **k):
        self.wsgi_app = lambda environ, start_response: None
    def route(self, *a, **k): return lambda f: f


class _Resp:
    def __init__(self, tresc, kod=200, naglowki=None):
        self.tresc, self.kod, self.headers = tresc, kod, dict(naglowki or {})


class _Zadanie:
    authorization = None
    method = "GET"
    def get_json(self, silent=False): return None


flask = types.ModuleType("flask")
flask.Flask = _App
flask.Response = _Resp
flask.request = _Zadanie()
flask.send_from_directory = lambda katalog, sciezka: _Resp(f"PLIK:{sciezka}")
sys.modules["flask"] = flask

HASLO = "bardzo-tajne-haslo-2026"
SOL = secrets.token_bytes(16)
os.environ["PANEL_UZYTKOWNIK"] = "wlasciciel"
os.environ["PANEL_HASLO_HASH"] = (
    SOL.hex() + ":" + pbkdf2_hmac("sha256", HASLO.encode(), SOL, 240_000).hex()
)

sys.path.insert(0, str(PROJEKT))
import wsgi  # noqa: E402


class Dane:
    def __init__(self, uzytkownik, haslo):
        self.username, self.password = uzytkownik, haslo


def kod(odpowiedz) -> int:
    """serve() zwraca krotke (odpowiedz, kod); nasze funkcje panelu — sam obiekt."""
    if isinstance(odpowiedz, tuple):
        return odpowiedz[1]
    return odpowiedz.kod


def tresc(odpowiedz):
    return odpowiedz[0].tresc if isinstance(odpowiedz, tuple) else odpowiedz.tresc


def main() -> int:
    bledy = 0

    def sprawdz(opis, warunek):
        nonlocal bledy
        print(f"{'OK  ' if warunek else 'BLAD'}  {opis}")
        if not warunek:
            bledy += 1

    sprawdz("panel wlaczony, gdy sa obie zmienne", wsgi.panel_wlaczony())

    wsgi.request.authorization = None
    sprawdz("bez logowania: 401 na plik panelu", kod(wsgi.panel_pliki("panel.html")) == 401)
    sprawdz("bez logowania: 401 na API", kod(wsgi.panel_api("wczytaj")) == 401)
    sprawdz("401 niesie naglowek WWW-Authenticate",
            "WWW-Authenticate" in wsgi.panel_pliki("panel.html").headers)

    wsgi.request.authorization = Dane("wlasciciel", "zle-haslo")
    sprawdz("zle haslo: 401", kod(wsgi.panel_pliki("panel.html")) == 401)
    wsgi.request.authorization = Dane("ktos-inny", HASLO)
    sprawdz("zly uzytkownik: 401", kod(wsgi.panel_pliki("panel.html")) == 401)
    wsgi.request.authorization = Dane("wlasciciel", "")
    sprawdz("puste haslo: 401", kod(wsgi.panel_pliki("panel.html")) == 401)

    wsgi.request.authorization = Dane("wlasciciel", HASLO)
    odp = wsgi.panel_pliki("panel.html")
    sprawdz("poprawne haslo: plik oddany", tresc(odp) == "PLIK:tools/panel/panel.html")
    sprawdz("panel oznaczony noindex", odp.headers.get("X-Robots-Tag", "").startswith("noindex"))
    sprawdz("panel bez cache", odp.headers.get("Cache-Control") == "no-store")

    # nawet po zalogowaniu dostepne sa tylko trzy pliki interfejsu
    for plik in ("serwer.py", "haslo.py", "README.md", "../../wsgi.py"):
        sprawdz(f"po zalogowaniu {plik} nadal 404", kod(wsgi.panel_pliki(plik)) == 404)

    odp = wsgi.panel_api("wczytaj")
    sprawdz("API wczytaj zwraca cennik", kod(odp) == 200 and "cennik" in json.loads(tresc(odp)))
    sprawdz("nieznana akcja API: 404", kod(wsgi.panel_api("cokolwiek")) == 404)

    # brak konfiguracji = panelu nie ma; to musi byc 404, a nie 401,
    # zeby nie zdradzac, ze cokolwiek tu istnieje
    wsgi.PANEL_UZYTKOWNIK = ""
    wsgi.PANEL_HASLO_HASH = ""
    sprawdz("brak konfiguracji: 404 na plik", kod(wsgi.panel_pliki("panel.html")) == 404)
    sprawdz("brak konfiguracji: 404 na API", kod(wsgi.panel_api("wczytaj")) == 404)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
