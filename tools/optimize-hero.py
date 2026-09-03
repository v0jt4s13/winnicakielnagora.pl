#!/usr/bin/env python3
"""Przekodowuje klatki zdjecia wejsciowego (hero) z PNG na WebP.

Klatki pory dnia trafily do repozytorium jako PNG po ok. 2 MB kazda, a to wlasnie
zdjecie hero jest elementem LCP odslony strony glownej — jeden PNG tej wagi kasuje
caly zysk z wczesnego wykrycia obrazu przez preload scanner. WebP w tej samej
rozdzielczosci schodzi do ok. 1/13 rozmiaru bez widocznej roznicy.

PNG-i zostaja nietkniete: sa masterem, z ktorego mozna przekodowac ponownie.
Przegladarki bez obslugi WebP lapie istniejacy fallback na winnica-panorama-01.jpg
(atrybut data-fallback-src na <img id="hero-image">, obsluga w main.js).

Uruchomienie: python3 tools/optimize-hero.py
"""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
HERO = BASE / "attached_assets" / "photos" / "hero"

# q80 wybrane z pomiaru: q75 bywa juz widoczne na gladkim niebie, q85 kosztuje
# ok. 25% rozmiaru nie dajac nic w zamian.
JAKOSC = 80


def main() -> None:
    zrodla = sorted(HERO.glob("*.png"))
    if not zrodla:
        print(f"BRAK ZRODEL w {HERO.relative_to(BASE)}")
        return

    zrodlo_suma = wynik_suma = 0
    for png in zrodla:
        zrodlo_suma += png.stat().st_size
        obraz = Image.open(png).convert("RGB")
        webp = png.with_suffix(".webp")
        obraz.save(webp, "WEBP", quality=JAKOSC, method=6)
        wynik_suma += webp.stat().st_size
        print(f"{webp.name}  {obraz.size[0]}x{obraz.size[1]}  "
              f"{png.stat().st_size // 1024} KB -> {webp.stat().st_size // 1024} KB")

    print(f"\nzrodlo: {zrodlo_suma / 1024 / 1024:.1f} MB  ->  "
          f"wynik: {wynik_suma / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
