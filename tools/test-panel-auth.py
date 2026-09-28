#!/usr/bin/env python3
"""Testy uwierzytelniania panelu na produkcji, bez instalowania Flaska.

Panel na produkcji zapisuje pliki, wiec jego zabezpieczenia musza byc sprawdzalne.
Flask nie jest zainstalowany lokalnie (AGENTS.md → Commands), podstawiamy wiec atrape
i wolamy funkcje wsgi.py wprost.

Uruchomienie: python3 tools/test-panel-auth.py
"""
import atexit
import json
import os
import secrets
import shutil
import sys
import tempfile
import types
from hashlib import pbkdf2_hmac
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent


class _App:
    def __init__(self, *a, **k):
        self.wsgi_app = lambda environ, start_response: None
        self.config = {}
    def route(self, *a, **k): return lambda f: f
    def after_request(self, f): return f


class _Resp:
    def __init__(self, tresc, kod=200, naglowki=None):
        self.tresc, self.kod, self.headers = tresc, kod, dict(naglowki or {})


class _Zadanie:
    authorization = None
    method = "GET"
    script_root = ""
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

# Testy zapisu (dla konfliktu wersji) nie moga tykac prawdziwego data/wina.json —
# przekierowanie MUSI byc ustawione przed importem wsgi.py, bo cennik.py/wydarzenia.py
# czytaja CENNIK_SCIEZKA/WYDARZENIA_SCIEZKA raz, przy wlasnym imporcie.
KATALOG_TYMCZASOWY = Path(tempfile.mkdtemp(prefix="panel-auth-test-"))
os.environ["CENNIK_SCIEZKA"] = str(KATALOG_TYMCZASOWY / "wina.json")
os.environ["WYDARZENIA_SCIEZKA"] = str(KATALOG_TYMCZASOWY / "wydarzenia.json")
atexit.register(shutil.rmtree, KATALOG_TYMCZASOWY, ignore_errors=True)

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
    for akcja in ("galeria-wgraj", "galeria-usun"):
        sprawdz(f"bez logowania: 401 na {akcja}", kod(wsgi.panel_api(akcja)) == 401)
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

    # Zapis z nieaktualna wersja pliku musi zostac odrzucony (409), nie po cichu
    # nadpisany — to test naprawy wypadku z dwoma redaktorami naraz (TODO #39).
    wsgi.request.method = "POST"
    dane_do_zapisu = wsgi.cennik.wczytaj()
    wersja_przed = wsgi.cennik.wersja_pliku()

    wsgi.request.get_json = lambda silent=False: {
        "wersja": "wersja-widmo", "dane": dane_do_zapisu}
    odp = wsgi.panel_api("zapisz")
    sprawdz("zapis z nieaktualną wersją: 409", kod(odp) == 409)
    sprawdz("409 niesie konflikt=True", json.loads(tresc(odp)).get("konflikt") is True)
    sprawdz("odrzucony zapis nie dotknął pliku",
            wsgi.cennik.wersja_pliku() == wersja_przed)

    # Sama tresc musi sie realnie zmienic — identyczny zapis daje identyczny hash,
    # co nie dowodziloby niczego o samym mechanizmie wersjonowania.
    dane_zmienione = wsgi.cennik.wczytaj()
    dane_zmienione["wina"][0]["dostepne"] = not dane_zmienione["wina"][0]["dostepne"]
    wsgi.request.get_json = lambda silent=False: {
        "wersja": wersja_przed, "dane": dane_zmienione}
    odp = wsgi.panel_api("zapisz")
    sprawdz("zapis z właściwą wersją: 200", kod(odp) == 200)
    sprawdz("zapis z właściwą wersją faktycznie zmienił plik",
            wsgi.cennik.wersja_pliku() != wersja_przed)

    # Wgrywanie i usuwanie zdjec (SPEC-009) — do tymczasowego attached_assets, nie do repo.
    import io
    from PIL import Image
    poprzednie_zasoby = wsgi.galeria.ZASOBY
    wsgi.galeria.ZASOBY = KATALOG_TYMCZASOWY / "attached_assets"
    wsgi.galeria.ZASOBY.mkdir()
    bufor = io.BytesIO()
    Image.new("RGB", (40, 30), "red").save(bufor, "JPEG")
    wsgi.request.args = {"nazwa": "Butelka Nowa.jpg"}
    wsgi.request.get_data = lambda: bufor.getvalue()
    wsgi.request.content_length = wsgi.galeria.MAX_WGRYWANIE + 1
    sprawdz("wgrywanie ponad limit: 413", kod(wsgi.panel_api("galeria-wgraj")) == 413)
    wsgi.request.content_length = len(bufor.getvalue())
    odp = wsgi.panel_api("galeria-wgraj")
    sprawdz("wgrywanie po zalogowaniu: 200 i plik w uploads/",
            kod(odp) == 200 and json.loads(tresc(odp))["sciezka"] == "uploads/butelka-nowa.jpg"
            and (wsgi.galeria.ZASOBY / "uploads" / "butelka-nowa.jpg").is_file())
    wsgi.request.get_json = lambda silent=False: {"pliki": ["uploads/butelka-nowa.jpg"]}
    odp = wsgi.panel_api("galeria-usun")
    sprawdz("usuwanie po zalogowaniu: 200 i plik znika",
            kod(odp) == 200 and not (wsgi.galeria.ZASOBY / "uploads" / "butelka-nowa.jpg").exists())
    # /zdrowie pokazuje, gdzie fizycznie laduja zdjecia — dowiazanie rozwiniete do celu.
    (wsgi.galeria.ZASOBY / "uploads").rmdir()
    sprawdz("/zdrowie: brak katalogu uploads zaznaczony wprost",
            json.loads(tresc(wsgi.zdrowie()))["uploads"].startswith("brak katalogu"))
    cel_uploads = KATALOG_TYMCZASOWY / "dane-uploads"
    cel_uploads.mkdir()
    (wsgi.galeria.ZASOBY / "uploads").symlink_to(cel_uploads, target_is_directory=True)
    sprawdz("/zdrowie: uploads jako dowiązanie pokazuje cel",
            json.loads(tresc(wsgi.zdrowie()))["uploads"] == str(cel_uploads.resolve()))
    sprawdz("/zdrowie: brak katalogu pokoje zaznaczony wprost",
            json.loads(tresc(wsgi.zdrowie()))["pokoje"].startswith("brak katalogu"))
    wsgi.galeria.ZASOBY = poprzednie_zasoby

    sprawdz("globalny limit żądania = limit wgrywania",
            wsgi.app.config["MAX_CONTENT_LENGTH"] == wsgi.galeria.MAX_WGRYWANIE)
    wsgi.request.content_length = wsgi.kontakt.MAX_CIAZAR_ZADANIA + 1
    sprawdz("formularz kontaktowy nadal odrzuca > 16 KB (413)", kod(wsgi.formularz_kontaktowy()) == 413)
    del wsgi.request.content_length, wsgi.request.args, wsgi.request.get_data

    del wsgi.request.get_json  # przywraca domyslne z klasy _Zadanie (zwraca None)
    wsgi.request.method = "GET"

    # Uszkodzony hash nie moze udawac dzialajacego panelu. Zdarza sie, gdy wartosc
    # urwie sie na spacji przy przekazywaniu przez EXTRA_SYSTEMD_ENV.
    poprawny = wsgi.PANEL_HASLO_HASH
    for zly, opis in [
        ("<z", "obciety placeholder"),
        ("abc", "bez separatora"),
        ("aa:bb", "za krotki"),
        ("zzzz" * 8 + ":" + "zz" * 32, "nieszesnastkowy"),
    ]:
        wsgi.PANEL_HASLO_HASH = zly
        sprawdz(f"uszkodzony hash ({opis}): panel wylaczony", not wsgi.panel_wlaczony())
        sprawdz(f"uszkodzony hash ({opis}): 404, nie 401",
                kod(wsgi.panel_pliki("panel.html")) == 404)
    wsgi.PANEL_HASLO_HASH = poprawny
    sprawdz("poprawny hash: panel znow wlaczony", wsgi.panel_wlaczony())

    # brak konfiguracji = panelu nie ma; to musi byc 404, a nie 401,
    # zeby nie zdradzac, ze cokolwiek tu istnieje
    wsgi.PANEL_UZYTKOWNIK = ""
    wsgi.PANEL_HASLO_HASH = ""
    sprawdz("brak konfiguracji: 404 na plik", kod(wsgi.panel_pliki("panel.html")) == 404)
    sprawdz("brak konfiguracji: 404 na API", kod(wsgi.panel_api("wczytaj")) == 404)
    sprawdz("brak konfiguracji: 404 na galeria-wgraj", kod(wsgi.panel_api("galeria-wgraj")) == 404)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
