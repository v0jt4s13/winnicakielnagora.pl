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
        self.wsgi_app = lambda environ, start_response: None

    def route(self, *_, **__):
        return lambda funkcja: funkcja

    def after_request(self, funkcja):
        return funkcja


class _Resp:
    def __init__(self, tresc, kod=200, naglowki=None):
        self.tresc, self.kod, self.headers = tresc, kod, dict(naglowki or {})

    # Strona glowna wysyla ETag i odpowiada warunkowo. Werkzeug robi to sam, atrapa
    # musi tylko nie wywrocic sie na wywolaniu.
    def add_etag(self):
        self.headers["ETag"] = "atrapa"

    def make_conditional(self, _zadanie):
        return self


class _Zadanie:
    authorization = None
    method = "GET"
    script_root = ""
    args = {}          # ?hero=... — ten zestaw testuje adresy bez parametrow

    def get_json(self, silent=False):
        return None


def _send_from_directory(katalog, sciezka):
    return _Resp(f"PLIK:{sciezka}")


flask = types.ModuleType("flask")
flask.Flask = _App
flask.Response = _Resp
flask.request = _Zadanie()
flask.send_from_directory = _send_from_directory
sys.modules["flask"] = flask

sys.path.insert(0, str(PROJEKT))
import wsgi  # noqa: E402  (import po podstawieniu atrapy)


def wynik(sciezka: str) -> tuple[str, int]:
    """Zwraca (oddany_plik, kod_http) dla danego adresu.

    Strona bledu nie idzie przez send_from_directory — wsgi.strona_404() czyta ja sama,
    zeby podmienic <base> na przedrostek wdrozenia. Rozpoznajemy ja po kodzie 404.
    """
    odpowiedz = wsgi.serve(sciezka)
    if isinstance(odpowiedz, tuple):
        odpowiedz, kod = odpowiedz[0], odpowiedz[1]
    else:
        kod = getattr(odpowiedz, "kod", 200)
    if isinstance(odpowiedz, _Resp):
        if kod == 404:
            return "404.html", 404
        return odpowiedz.tresc, kod
    return odpowiedz, kod


PRZYPADKI = [
    # adres,                          oczekiwany plik,               kod
    # "/" nie idzie przez send_from_directory (podmiana hero) — patrz sprawdz_hero()
    ("index.html",                    "index.html",                  200),
    ("wina/monarch.html",             "wina/monarch.html",           200),
    ("wina/soki.html",                "wina/soki.html",              200),
    # /data/wina.json obsluguje osobna trasa zywy_cennik(), nie catch-all — sprawdza to
    # tools/test-cennik-sciezka.py. Tutaj katalog data/ ma byc niedostepny.
    ("data/wina.json",                "404.html",                    404),
    ("data/cokolwiek.txt",            "404.html",                    404),
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
    # panel jest za haslem: bez PANEL_UZYTKOWNIK/PANEL_HASLO_HASH nie istnieje.
    # Uwierzytelnianie sprawdza osobno tools/test-panel-auth.py
    ("tools/panel/panel.html",        "404.html",                    404),
    ("tools/panel/panel.css",         "404.html",                    404),
    ("tools/panel/panel.js",          "404.html",                    404),
    ("tools/panel/README.md",         "404.html",                    404),
    ("tools/panel",                   "404.html",                    404),
    ("tools",                         "404.html",                    404),
    ("404.html",                      "404.html",                    200),
]


def sprawdz_hero() -> int:
    """Strona glowna musi wskazac klatke hero juz w HTML-u, a ?hero nie moze klamac."""
    bledy = 0

    def sprawdz(opis, warunek):
        nonlocal bledy
        print(f"{'OK  ' if warunek else 'BLAD'}  {opis}")
        if not warunek:
            bledy += 1

    # --- siatka godzin: musi zgadzac sie z heroPeriodForHour() w assets/js/main.js ---
    for godzina, oczekiwana in ((0, "noc"), (5, "noc"), (6, "poranek"), (11, "poranek"),
                                (12, "dzien"), (17, "dzien"), (18, "zachod"),
                                (21, "zachod"), (22, "noc"), (23, "noc")):
        sprawdz(f"godzina {godzina:02d} → {oczekiwana}",
                wsgi._pora_hero(godzina) == oczekiwana)

    # --- zwykle wejscie na "/" ---
    wsgi.request.args = {}
    odpowiedz = wsgi.serve("")
    tresc = odpowiedz.tresc
    pora = wsgi._pora_hero_teraz()
    zdjecie = f"./attached_assets/photos/hero/{pora}.webp"
    sprawdz(f'"/" ma src na <img> ({pora})',
            f'<img id="hero-image" src="{zdjecie}"' in tresc)
    sprawdz('"/" ma preload na te sama klatke',
            f'<link rel="preload" as="image" href="{zdjecie}" fetchpriority="high">' in tresc)
    sprawdz('"/" nie zostawia nieuzytego znacznika',
            wsgi.HERO_KOTWICA_PRELOAD not in tresc)
    sprawdz('"/" nie preloaduje zdjecia zapasowego',
            'as="image" href="./attached_assets/photos/winnica-panorama-01.jpg"' not in tresc)
    sprawdz('"/" wymusza rewalidacje', odpowiedz.headers.get("Cache-Control") == "no-cache")
    sprawdz('"/" bez paska wyboru pory', "data-hero-kandydaci" not in tresc)

    # --- narzedzie pomiarowe ?hero= ---
    wsgi.request.args = {"hero": "noc"}
    tresc = wsgi.serve("").tresc
    sprawdz('?hero=noc podmienia klatke',
            '<img id="hero-image" src="./attached_assets/photos/hero/noc.webp"' in tresc)
    sprawdz('?hero=noc pokazuje pasek wyboru', "data-hero-kandydaci" in tresc)

    wsgi.request.args = {"hero": "../../etc/passwd"}
    tresc = wsgi.serve("").tresc
    # Uwaga na skrot: sam 'src="./attached_assets/photos/hero/' wystepuje takze w
    # data-poranek-src=... — kotwiczymy sie wiec na calym poczatku znacznika <img>.
    sprawdz("?hero z niedozwolona wartoscia nie podmienia niczego",
            f'{wsgi.HERO_KOTWICA_IMG} src=' not in tresc)
    sprawdz("?hero z niedozwolona wartoscia daje sam pasek",
            "data-hero-kandydaci" in tresc)
    wsgi.request.args = {}

    # --- kotwica przestala pasowac ---
    sprawdz("brak kotwicy → None, a nie po cichu ta sama tresc",
            wsgi._wstrzyknij_hero("<html>bez hero</html>", "noc") is None)
    sprawdz("podwojna kotwica tez → None",
            wsgi._wstrzyknij_hero(wsgi.HERO_KOTWICA_IMG * 2 + wsgi.HERO_KOTWICA_PRELOAD,
                                  "noc") is None)
    return bledy


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

    # Strona bledu musi dostac <base> zgodny z przedrostkiem wdrozenia, bo bywa serwowana
    # pod dowolnie gleboka sciezka — inaczej szuka CSS i JS w zlym miejscu.
    for przedrostek, oczekiwany_base in (("", '<base href="/">'),
                                         ("/winnicakielnagora.pl", '<base href="/winnicakielnagora.pl/">')):
        wsgi.request.script_root = przedrostek
        tresc = wsgi.strona_404().tresc
        opis = przedrostek or "korzen domeny"
        ok = oczekiwany_base in tresc
        print(f"{'OK  ' if ok else 'BLAD'}  404 pod {opis}: {oczekiwany_base}")
        if not ok:
            bledy += 1
        if 'href="/assets' in tresc or 'src="/assets' in tresc:
            print("BLAD  404 ma sciezki bezwzgledne od korzenia hosta")
            bledy += 1
    wsgi.request.script_root = ""

    bledy += sprawdz_hero()

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
