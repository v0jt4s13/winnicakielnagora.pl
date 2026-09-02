import hashlib
import hmac
import json
import os
from hashlib import pbkdf2_hmac
from pathlib import Path

from flask import Flask, Response, request, send_from_directory

import cennik

BASE = Path(__file__).parent
STATIC_CANDIDATES = [BASE / "dist" / "public", BASE]  # wybierz dist/public po buildzie, inaczej katalog repo
STATIC_ROOT = next((p for p in STATIC_CANDIDATES if p.exists()), BASE)

app = Flask(__name__, static_folder=None)  # statyki wydajemy sami, przez serve()


# Witryna bywa serwowana pod podsciezka (dev stoi pod /winnicakielnagora.pl/). Jesli proxy
# nie obcina przedrostka, trasy zapisane od korzenia nie dopasuja sie do niczego. Ta warstwa
# obcina go sama, gdy ustawisz SCIEZKA_BAZOWA; honoruje tez SCRIPT_NAME, ktory wysyla
# wiekszosc poprawnie skonfigurowanych proxy.
SCIEZKA_BAZOWA = "/" + os.environ.get("SCIEZKA_BAZOWA", "").strip().strip("/")


class ObetnijPrzedrostek:
    def __init__(self, aplikacja):
        self.aplikacja = aplikacja

    def __call__(self, environ, start_response):
        przedrostek = environ.get("SCRIPT_NAME") or (
            SCIEZKA_BAZOWA if SCIEZKA_BAZOWA != "/" else ""
        )
        sciezka = environ.get("PATH_INFO", "")
        if przedrostek and sciezka.startswith(przedrostek):
            environ["PATH_INFO"] = sciezka[len(przedrostek):] or "/"
            environ["SCRIPT_NAME"] = przedrostek
        return self.aplikacja(environ, start_response)


app.wsgi_app = ObetnijPrzedrostek(app.wsgi_app)


# Katalogiem statycznym jest caly katalog repozytorium, wiec bez tej listy publicznie
# dostepne bylyby takze wsgi.py, AGENTS.md, TODO.md, tools/ oraz .git/ z cala historia.
# Wpuszczamy tylko to, co ma trafic do przegladarki.
PLIKI_PUBLICZNE = {"index.html", "404.html", "sitemap.xml", "robots.txt", "favicon.ico", "favicon.svg"}
# `data` nie ma tu wpisu celowo: /data/wina.json obsluguje osobna trasa, ktora czyta
# plik roboczy spoza katalogu wdrozenia.
KATALOGI_PUBLICZNE = {"assets", "attached_assets", "wina", "filmy"}
# Z calego tools/ dostepne sa wylacznie te trzy pliki — i to za haslem (patrz PANEL_*).
PLIKI_PANELU = {"tools/panel/panel.html", "tools/panel/panel.css", "tools/panel/panel.js"}


def _publiczna(wzgledna: Path) -> bool:
    czesci = wzgledna.parts
    if not czesci or any(czesc.startswith(".") for czesc in czesci):
        return False
    if wzgledna.suffix == ".bak":
        return False
    if len(czesci) == 1:
        return czesci[0] in PLIKI_PUBLICZNE
    return czesci[0] in KATALOGI_PUBLICZNE


def _plik(sciezka: str) -> str | None:
    """Zwraca sciezke wzgledna, jesli wskazuje istniejacy, publiczny plik w STATIC_ROOT.

    resolve() rozwija dowiazania symboliczne przed sprawdzeniem — samo obciecie ".."
    nie wystarcza.
    """
    if not sciezka:
        return None
    kandydat = (STATIC_ROOT / sciezka).resolve()
    korzen = STATIC_ROOT.resolve()
    if not (kandydat.is_file() and kandydat.is_relative_to(korzen)):
        return None
    wzgledna = kandydat.relative_to(korzen)
    return str(wzgledna) if _publiczna(wzgledna) else None


# --- panel redakcyjny na produkcji ---------------------------------------------
# Wlacza sie WYLACZNIE gdy ustawione sa PANEL_UZYTKOWNIK i PANEL_HASLO_HASH.
# Bez nich kazde /tools/panel/... dostaje 404, jakby panelu nie bylo — brak
# konfiguracji nie moze przypadkiem odslonic zapisu do pliku.
#
# Hash generujesz poleceniem:  python3 tools/panel/haslo.py
PANEL_UZYTKOWNIK = os.environ.get("PANEL_UZYTKOWNIK", "").strip()
PANEL_HASLO_HASH = os.environ.get("PANEL_HASLO_HASH", "").strip()
PANEL_ITERACJE = 240_000


def panel_wlaczony() -> bool:
    return bool(PANEL_UZYTKOWNIK and PANEL_HASLO_HASH)


def _haslo_zgodne(uzytkownik: str, haslo: str) -> bool:
    """Porownanie odporne na pomiar czasu. Format hasha: sol:hash (obie czesci szesnastkowo).

    Separator to dwukropek, a nie dolar — hash przechodzi przez plik .env czytany przez
    basha i przez Environment= w unicie systemd, gdzie "$" ma wlasne znaczenie.
    """
    try:
        sol_hex, oczekiwany_hex = PANEL_HASLO_HASH.split(":", 1)
        sol = bytes.fromhex(sol_hex)
    except ValueError:
        return False
    policzony = pbkdf2_hmac("sha256", haslo.encode("utf-8"), sol, PANEL_ITERACJE)
    zgodny_uzytkownik = hmac.compare_digest(uzytkownik, PANEL_UZYTKOWNIK)
    zgodne_haslo = hmac.compare_digest(policzony.hex(), oczekiwany_hex)
    return zgodny_uzytkownik and zgodne_haslo


def _prosba_o_haslo():
    return Response(
        "Panel redakcyjny wymaga logowania.", 401,
        {"WWW-Authenticate": 'Basic realm="Panel cennika", charset="UTF-8"'},
    )


def _zalogowany() -> bool:
    dane = request.authorization
    return bool(dane and dane.username and dane.password
                and _haslo_zgodne(dane.username, dane.password))


def _json(dane: dict, kod: int = 200):
    return Response(json.dumps(dane, ensure_ascii=False), kod,
                    {"Content-Type": "application/json; charset=utf-8",
                     "Cache-Control": "no-store"})


@app.route("/zdrowie")
def zdrowie():
    """Punkt kontrolny: czy dziala TEN kod, a nie starsza kopia w pamieci procesu.

    Zwraca skrot z wsgi.py i cennik.py. Porownaj z wynikiem lokalnego:
        python3 -c "import hashlib,pathlib; print(hashlib.sha256(b''.join(pathlib.Path(p).read_bytes() for p in ('wsgi.py','cennik.py'))).hexdigest()[:12])"
    Rozne wartosci = serwer trzyma inny kod, niz jest w repozytorium.
    """
    znacznik = hashlib.sha256(
        b"".join((BASE / p).read_bytes() for p in ("wsgi.py", "cennik.py"))
    ).hexdigest()[:12]
    return _json({
        "ok": True,
        "znacznik_kodu": znacznik,
        "panel_wlaczony": panel_wlaczony(),
        "cennik": str(cennik.CENNIK),
        "sciezka_bazowa": SCIEZKA_BAZOWA,
    })


@app.route("/data/wina.json")
def zywy_cennik():
    """Cennik czytamy ze sciezki roboczej (CENNIK_SCIEZKA), a nie z kopii w repozytorium.

    Dzieki temu wdrozenie moze pomijac katalog data/ i nie kasuje cen wpisanych przez
    panel — wariant A z TODO #26.
    """
    cennik.zapewnij_plik()
    if not cennik.CENNIK.is_file():
        return _json({"waluta": "PLN", "stawka_vat": 0.23, "kategorie": [], "wina": []})
    odpowiedz = send_from_directory(cennik.CENNIK.parent, cennik.CENNIK.name)
    odpowiedz.headers["Cache-Control"] = "no-store"
    odpowiedz.headers["Content-Type"] = "application/json; charset=utf-8"
    return odpowiedz


@app.route("/tools/panel/api/<akcja>", methods=["GET", "POST"])
def panel_api(akcja: str):
    if not panel_wlaczony():
        return serve("nieistniejacy-adres")
    if not _zalogowany():
        return _prosba_o_haslo()

    if akcja == "wczytaj" and request.method == "GET":
        try:
            cennik.zapewnij_plik()
            return _json(cennik.stan_poczatkowy())
        except json.JSONDecodeError as blad:
            return _json({"ok": False, "komunikat": f"data/wina.json ma błąd składni: {blad}"}, 500)

    if akcja == "zapisz" and request.method == "POST":
        dane = request.get_json(silent=True)
        if dane is None:
            return _json({"ok": False, "bledy": [
                {"pozycja": None, "pole": None, "komunikat": "Nieczytelne żądanie"}]}, 400)
        bledy = cennik.waliduj(dane)
        if bledy:
            return _json({"ok": False, "bledy": bledy}, 400)
        try:
            cennik.zapisz(dane)
        except OSError as blad:
            return _json({"ok": False, "komunikat": f"Nie udało się zapisać: {blad}"}, 500)
        return _json({"ok": True, "pozycji": len(dane["wina"]),
                      "kopia": str(cennik.KOPIA.relative_to(cennik.PROJEKT))})

    return _json({"ok": False, "komunikat": "Nieznana akcja"}, 404)


@app.route("/tools/panel/<path:plik>")
def panel_pliki(plik: str):
    wzgledna = f"tools/panel/{plik}"
    if not panel_wlaczony() or wzgledna not in PLIKI_PANELU:
        return serve("nieistniejacy-adres")
    if not _zalogowany():
        return _prosba_o_haslo()
    odpowiedz = send_from_directory(STATIC_ROOT, wzgledna)
    odpowiedz.headers["Cache-Control"] = "no-store"
    odpowiedz.headers["X-Robots-Tag"] = "noindex, nofollow"
    return odpowiedz


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str):
    if not path:
        return send_from_directory(STATIC_ROOT, "index.html")

    istniejacy = _plik(path)
    if istniejacy:
        return send_from_directory(STATIC_ROOT, istniejacy)

    # Ladniejsze adresy: /wina/monarch obsluguje wina/monarch.html.
    # Uwaga: `python3 -m http.server` tego nie robi, dlatego linki w HTML-u
    # zostaja z rozszerzeniem .html — dzialaja i lokalnie, i na produkcji.
    bez_ukosnika = path.rstrip("/")
    if not Path(bez_ukosnika).suffix:
        for kandydat in (f"{bez_ukosnika}.html", f"{bez_ukosnika}/index.html"):
            istniejacy = _plik(kandydat)
            if istniejacy:
                return send_from_directory(STATIC_ROOT, istniejacy)

    # Nieznany adres to blad, a nie strona glowna. Wczesniej kazda literowka
    # dostawala index.html ze statusem 200, przez co wyszukiwarki widzialy
    # duplikaty strony glownej pod dowolnym adresem.
    strona_bledu = _plik("404.html")
    if strona_bledu:
        return send_from_directory(STATIC_ROOT, strona_bledu), 404
    return "Nie znaleziono strony", 404
