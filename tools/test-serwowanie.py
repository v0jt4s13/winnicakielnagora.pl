#!/usr/bin/env python3
"""Testy serwowania na PRAWDZIWYM Flasku: kompresja, nagłówki cache, strona 404.

Pozostałe zestawy (`test-routing.py`, `test-panel-auth.py`) podstawiają atrapę Flaska,
żeby dało się je uruchomić bez instalowania czegokolwiek. Atrapa nie odtwarza jednak
zachowań Werkzeuga — i to się zemściło: kompresja napisana pod atrapę zwracała 500 dla
każdego pliku tekstowego, bo `send_file` oddaje odpowiedź w trybie strumieniowym.
Ten zestaw łapie właśnie takie rzeczy.

Flask nie jest zainstalowany lokalnie (patrz AGENTS.md → Commands), więc test sam się
pomija, jeśli go nie znajdzie. Żeby go uruchomić:

    python3 -m venv /tmp/venv-test && /tmp/venv-test/bin/pip -q install flask
    /tmp/venv-test/bin/python tools/test-serwowanie.py
"""
import sys
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent

try:
    import flask  # noqa: F401
except ImportError:
    print("POMINIETO — Flask nie jest zainstalowany.")
    print("  python3 -m venv /tmp/venv-test && /tmp/venv-test/bin/pip -q install flask")
    print("  /tmp/venv-test/bin/python tools/test-serwowanie.py")
    sys.exit(0)

sys.path.insert(0, str(PROJEKT))
import wsgi  # noqa: E402

bledy = 0


def sprawdz(opis, warunek):
    global bledy
    print(f"{'OK  ' if warunek else 'BLAD'}  {opis}")
    if not warunek:
        bledy += 1


def main() -> int:
    k = wsgi.app.test_client()

    # --- kompresja tekstu -----------------------------------------------------
    for adres, nazwa in [("/", "index.html"), ("/assets/css/style.css", "style.css"),
                         ("/assets/js/main.js", "main.js"), ("/wina/monarch.html", "strona odmiany")]:
        r = k.get(adres, headers={"Accept-Encoding": "gzip"})
        sprawdz(f"{nazwa}: 200", r.status_code == 200)
        sprawdz(f"{nazwa}: skompresowany", r.headers.get("Content-Encoding") == "gzip")

    # Regresja: send_file oddaje odpowiedz strumieniowo i get_data() rzuca wyjatkiem,
    # jesli nie wylaczy sie direct_passthrough. Objawia sie kodem 500 na kazdym pliku.
    sprawdz("pliki tekstowe nie wywalaja sie na trybie strumieniowym",
            all(k.get(u, headers={"Accept-Encoding": "gzip"}).status_code == 200
                for u in ("/", "/assets/css/custom.css", "/assets/js/produkty.js")))

    # --- czego kompresowac nie wolno -----------------------------------------
    r = k.get("/attached_assets/photos/winnica-panorama-01.jpg", headers={"Accept-Encoding": "gzip"})
    sprawdz("JPEG bez kompresji", r.headers.get("Content-Encoding") is None)

    r = k.get("/assets/css/style.css")
    sprawdz("klient bez gzip dostaje wersje surowa", r.headers.get("Content-Encoding") is None)
    sprawdz("Vary: Accept-Encoding obecny", "Accept-Encoding" in (r.headers.get("Vary") or ""))

    # --- naglowki cache -------------------------------------------------------
    przypadki = [
        ("/", "no-cache", "HTML musi byc swiezy"),
        ("/assets/css/style.css", "no-cache", "CSS bez max-age — patrz TODO #35"),
        ("/assets/js/main.js", "no-cache", "JS bez max-age"),
        ("/attached_assets/photos/winnica-panorama-01.jpg", "max-age=2592000", "zdjecia"),
        ("/data/wina.json", "no-store", "cennik zmieniany panelem"),
    ]
    for adres, oczekiwane, opis in przypadki:
        cc = k.get(adres).headers.get("Cache-Control", "")
        sprawdz(f"cache {opis}: {oczekiwane}", oczekiwane in cc)

    # --- strona 404 -----------------------------------------------------------
    r = k.get("/nie-ma-takiej-strony")
    sprawdz("nieznany adres: 404", r.status_code == 404)
    tresc = r.data.decode("utf-8")
    sprawdz("404 bez sciezek bezwzglednych od korzenia hosta",
            '="/assets' not in tresc and '="/attached_assets' not in tresc)
    sprawdz("404 w korzeniu ma base /", '<base href="/">' in tresc)

    r = k.get("/nie-ma", environ_overrides={"SCRIPT_NAME": "/winnicakielnagora.pl"})
    sprawdz("404 pod prefiksem ma base z prefiksem",
            '<base href="/winnicakielnagora.pl/">' in r.data.decode("utf-8"))

    # --- co nadal ma byc zamkniete -------------------------------------------
    for adres in ("/wsgi.py", "/cennik.py", "/.git/config", "/TODO.md", "/tools/panel/serwer.py"):
        sprawdz(f"{adres} niedostepny", k.get(adres).status_code == 404)

    print("\nWSZYSTKIE TESTY PRZESZLY" if bledy == 0 else f"\n{bledy} TESTOW NIE PRZESZLO")
    return 0 if bledy == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
