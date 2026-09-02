#!/usr/bin/env python3
"""Pobiera fonty z Google Fonts do assets/fonts/ i generuje reguly @font-face.

Po co: dopoki fonty ida z fonts.googleapis.com, sciezka krytyczna to dwa obce originy
(DNS + TCP + TLS), blokujacy render arkusz i dopiero potem pliki woff2. Self-hosting
usuwa z tego trzy–cztery podroze w sieci.

Uruchomienie:  python3 tools/pobierz-fonty.py
Wynik:         assets/fonts/*.woff2 + assets/fonts/fonty.css do wklejenia w custom.css

Pobieramy WYLACZNIE podzbiory latin i latin-ext — polskie znaki (ą ę ł ń ś ź ż) siedza
w latin-ext. Cyrylica i wietnamski to kilkadziesiat kB, ktorych ta witryna nie uzywa.

Playfair Display i Lato sa na licencji OFL, ktora pozwala na redystrybucje pod warunkiem
zachowania noty licencyjnej — patrz assets/fonts/OFL.txt.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent
KATALOG = PROJEKT / "assets" / "fonts"

# Kroje faktycznie uzywane w HTML i w produkty.js: font-medium (500) nie wystepuje
# na Playfair, a Lato 300/900 nie wystepuje nigdzie.
ADRES = ("https://fonts.googleapis.com/css2"
         "?family=Playfair+Display:wght@400;600;700&family=Lato:wght@400;700&display=swap")
PODZBIORY = {"latin", "latin-ext"}
UA_NOWOCZESNY = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def pobierz(adres: str, user_agent: str | None = None) -> bytes:
    """Pobiera przez curl — w niektorych srodowiskach Python nie ma dostepu do sieci,
    a curl jest zwykle przepuszczany przez posrednika."""
    if not shutil.which("curl"):
        raise SystemExit("Potrzebny jest curl.")
    polecenie = ["curl", "-sSL", "--max-time", "30", "--fail"]
    if user_agent:
        polecenie += ["-A", user_agent]
    wynik = subprocess.run(polecenie + [adres], capture_output=True)
    if wynik.returncode != 0:
        raise SystemExit(f"Nie udalo sie pobrac {adres}: {wynik.stderr.decode().strip()}")
    return wynik.stdout


def main() -> int:
    KATALOG.mkdir(parents=True, exist_ok=True)
    css = pobierz(ADRES, UA_NOWOCZESNY).decode("utf-8")

    bloki = re.findall(r"/\*\s*([\w\[\]-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S)
    if not bloki:
        print("Nie udalo sie odczytac blokow @font-face — czy adres jest aktualny?")
        return 1

    reguly, pobrane = [], 0
    for podzbior, blok in bloki:
        if podzbior not in PODZBIORY:
            continue
        rodzina = re.search(r"font-family:\s*'([^']+)'", blok).group(1)
        waga = re.search(r"font-weight:\s*(\d+)", blok).group(1)
        zakres = re.search(r"unicode-range:\s*([^;]+);", blok).group(1).strip()
        url = re.search(r"url\((https://[^)]+\.woff2)\)", blok).group(1)

        nazwa = f"{rodzina.lower().replace(' ', '-')}-{waga}-{podzbior}.woff2"
        (KATALOG / nazwa).write_bytes(pobierz(url))
        pobrane += 1
        print(f"  {nazwa:<44}{(KATALOG / nazwa).stat().st_size / 1024:6.1f} kB")

        reguly.append(
            f"@font-face {{\n"
            f"  font-family: '{rodzina}';\n"
            f"  font-style: normal;\n"
            f"  font-weight: {waga};\n"
            f"  font-display: swap;\n"
            f"  src: url('../fonts/{nazwa}') format('woff2');\n"
            f"  unicode-range: {zakres};\n"
            f"}}"
        )

    (KATALOG / "fonty.css").write_text(
        "/* Wygenerowane przez tools/pobierz-fonty.py — nie edytuj recznie. */\n"
        + "\n".join(reguly) + "\n", encoding="utf-8")

    suma = sum(p.stat().st_size for p in KATALOG.glob("*.woff2")) / 1024
    print(f"\nPobrano {pobrane} plikow, razem {suma:.0f} kB")
    print("Reguly: assets/fonts/fonty.css — wklej je na poczatek assets/css/custom.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())
