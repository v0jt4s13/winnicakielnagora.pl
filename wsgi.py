from pathlib import Path

from flask import Flask, send_from_directory

BASE = Path(__file__).parent
STATIC_CANDIDATES = [BASE / "dist" / "public", BASE]  # wybierz dist/public po buildzie, inaczej katalog repo
STATIC_ROOT = next((p for p in STATIC_CANDIDATES if p.exists()), BASE)

app = Flask(__name__, static_folder=str(STATIC_ROOT), static_url_path="")


# Katalogiem statycznym jest caly katalog repozytorium, wiec bez tej listy publicznie
# dostepne bylyby takze wsgi.py, AGENTS.md, TODO.md, tools/ oraz .git/ z cala historia.
# Wpuszczamy tylko to, co ma trafic do przegladarki.
PLIKI_PUBLICZNE = {"index.html", "404.html", "sitemap.xml", "robots.txt", "favicon.ico"}
KATALOGI_PUBLICZNE = {"assets", "attached_assets", "wina", "data"}


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
