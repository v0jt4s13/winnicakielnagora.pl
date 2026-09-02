#!/usr/bin/env python3
"""Przeskalowuje zdjecia z docs/materialy-do-wykorzystania/ do attached_assets/photos/.

Oryginaly zostaja nietkniete. Dla kazdego zdjecia powstaja dwa pliki:
  <slug>.jpg     - dluzszy bok 1600 px, do sekcji i stron win
  <slug>-sm.jpg  - dluzszy bok 600 px, do kart i miniatur

Slug z czlonem "-osoby-" oznacza zdjecie z rozpoznawalna osoba (patrz TODO.md - zgody
na wizerunek nie sa jeszcze potwierdzone).

Uruchomienie: python3 tools/optimize-photos.py
"""
from pathlib import Path

from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "docs" / "materialy-do-wykorzystania"
DST = BASE / "attached_assets" / "photos"

# zrodlo -> slug docelowy
MAPA = {
    "Dornfelder/DSC_4763.jpg": "dornfelder-kiscie-01",
    "Dornfelder/DSC_4902.jpg": "dornfelder-kieliszek-01",
    "Dornfelder/DSC_5426.jpg": "dornfelder-zbiory-osoby-01",
    "Dornfelder/DSC_5556.jpg": "dornfelder-zbiory-osoby-02",
    "Monarch/DSC_4894.jpg": "monarch-kieliszek-01",
    "Monarch/DSC_5256.jpg": "monarch-butelka-01",
    "Monarch/DSC_5536.jpg": "monarch-zbiory-osoby-01",
    "Monarch/DSC_5548.jpg": "monarch-zbiory-osoby-02",
    "Monarch/DSC_5455-2.png": "monarch-zbiory-osoby-03",
    "Seyval Blanc/DSC_5203.jpg": "seyval-blanc-kieliszki-01",
    "Souvignier Gris/20250922_143105.jpg": "souvignier-gris-kiscie-01",
    "Souvignier Gris/20250922_143111.jpg": "souvignier-gris-liscie-01",
    "Souvignier Gris/DSC_0931.jpg": "souvignier-gris-kiscie-02",
    "St_Pepin/DSC_4772.jpg": "st-pepin-kiscie-01",
    "St_Pepin/DSC_4792.jpg": "st-pepin-kiscie-02",
    "St_Pepin/IMG_4502.JPG": "st-pepin-winnica-01",
    "St_Pepin/IMG_4508.JPG": "st-pepin-winnica-02",
    "Swenson Red/20251007_152554.jpg": "swenson-red-kiscie-01",
    "Swenson Red/20251007_152557.jpg": "swenson-red-kiscie-02",
    "Vidal Blanc/DSC_4772.jpg": "vidal-blanc-kiscie-01",
    "Vidal Blanc/DSC_4776.jpg": "vidal-blanc-kiscie-02",
    "Vidal Blanc/DSC_4814.jpg": "vidal-blanc-kiscie-03",
    "Vidal Blanc/DSC_5248.jpg": "vidal-blanc-zbiory-01",
    "zbiory_i_winnica/20250922_142706.jpg": "winnica-budynek-01",
    "zbiory_i_winnica/DSC_0013.jpg": "winnica-transport-osoby-01",
    "zbiory_i_winnica/DSC_0044.jpg": "winnica-zbiory-osoby-01",
    "zbiory_i_winnica/DSC_0046.jpg": "winnica-zbiory-osoby-02",
    "zbiory_i_winnica/DSC_0050.jpg": "winnica-zbiory-osoby-03",
    "zbiory_i_winnica/DSC_0665.jpg": "winnica-skrzynie-osoby-01",
    "zbiory_i_winnica/DSC_0669.jpg": "winnica-skrzynie-osoby-02",
    "zbiory_i_winnica/DSC_0691.jpg": "winnica-rzedy-01",
    "zbiory_i_winnica/DSC_0699.jpg": "winnica-zbiory-osoby-04",
    "zbiory_i_winnica/DSC_4885.jpg": "winnica-butelka-biale-01",
    "zbiory_i_winnica/DSC_4914.jpg": "winnica-butelka-czerwone-01",
    "zbiory_i_winnica/DSC_5336.jpg": "winnica-panorama-01",
    "zbiory_i_winnica/DSC_5505-2.jpg": "winnica-zbiory-osoby-05",
    "zbiory_i_winnica/DSC_5517.jpg": "winnica-zbiory-osoby-06",
    "zbiory_i_winnica/DSC_8993.jpg": "winnica-goscie-osoby-01",
    "zbiory_i_winnica/DSC_9009.jpg": "winnica-goscie-osoby-02",
    "zbiory_i_winnica/DSC_9022.jpg": "winnica-goscie-osoby-03",
    "zbiory_i_winnica/DSC_9052.jpg": "winnica-goscie-osoby-04",
}

WARIANTY = [("", 1600, 82), ("-sm", 600, 80)]


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    zrodlo_suma = wynik_suma = 0

    for wzgledna, slug in sorted(MAPA.items(), key=lambda kv: kv[1]):
        src = SRC / wzgledna
        if not src.exists():
            print(f"BRAK ZRODLA: {wzgledna}")
            continue
        zrodlo_suma += src.stat().st_size

        oryginal = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        for sufiks, bok, jakosc in WARIANTY:
            im = oryginal.copy()
            im.thumbnail((bok, bok), Image.LANCZOS)
            out = DST / f"{slug}{sufiks}.jpg"
            im.save(out, "JPEG", quality=jakosc, optimize=True, progressive=True)
            wynik_suma += out.stat().st_size
            print(f"{slug}{sufiks}.jpg  {im.size[0]}x{im.size[1]}  {out.stat().st_size // 1024} KB")

    print(f"\nzrodlo: {zrodlo_suma / 1024 / 1024:.1f} MB  ->  wynik: {wynik_suma / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
