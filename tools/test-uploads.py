#!/usr/bin/env python3
"""Testy wgrywania i usuwania zdjec w attached_assets/uploads/ (SPEC-009).

Wszystko na tymczasowych katalogach: attached_assets, cennik i wydarzenia. `uploads`
sprawdzamy w obu postaciach — zwyklego katalogu (lokalnie) i dowiazania poza
attached_assets (produkcja: dane/uploads).
"""
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

_TMP = TemporaryDirectory()
DANE = Path(_TMP.name) / "dane"
DANE.mkdir()
# Przed importem cennik/wydarzenia — sciezki zywych danych czytane sa przy imporcie.
os.environ["CENNIK_SCIEZKA"] = str(DANE / "wina.json")
os.environ["WYDARZENIA_SCIEZKA"] = str(DANE / "wydarzenia.json")

from PIL import Image  # noqa: E402
import cennik  # noqa: E402
import galeria  # noqa: E402
import wydarzenia  # noqa: E402


def sprawdz(opis: str, warunek: bool) -> None:
    if not warunek:
        raise AssertionError(opis)
    print(f"OK    {opis}")


def odrzuca(opis: str, funkcja, wyjatek=ValueError) -> None:
    try:
        funkcja()
    except wyjatek:
        sprawdz(opis, True)
    else:
        sprawdz(opis, False)


def bajty(obraz: Image.Image, format_: str, **opcje) -> bytes:
    bufor = io.BytesIO()
    obraz.save(bufor, format_, **opcje)
    return bufor.getvalue()


def jpg_z_gps() -> bytes:
    obraz = Image.new("RGB", (4000, 3000), "red")
    exif = Image.Exif()
    exif[0x010F] = "Telefon"          # Make
    exif[0x8825] = {1: "N", 2: (50.0, 1.0, 1.0)}  # GPSInfo
    return bajty(obraz, "JPEG", exif=exif)


def testy_wgrywania(zasoby: Path) -> None:
    wynik = galeria.wgraj("Zdjęcie Butelki (kopia).JPG", jpg_z_gps())
    plik = zasoby / wynik["sciezka"]
    sprawdz("zapis w uploads/ ze slugiem", wynik["sciezka"] == "uploads/zdjecie-butelki-kopia.jpg")
    with Image.open(plik) as obraz:
        sprawdz("dłuższy bok zmniejszony do 2000 px", max(obraz.size) == 2000)
        sprawdz("wymiary w odpowiedzi zgadzają się z plikiem", obraz.size == (wynik["szerokosc"], wynik["wysokosc"]))
        sprawdz("EXIF usunięty (brak GPS i modelu)", len(obraz.getexif()) == 0)

    drugi = galeria.wgraj("Zdjęcie Butelki (kopia).jpg", jpg_z_gps())
    sprawdz("kolizja nazwy -> -2, bez nadpisania", drugi["sciezka"] == "uploads/zdjecie-butelki-kopia-2.jpg")

    alfa = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    sprawdz("PNG z przezroczystością -> .webp", galeria.wgraj("logo.png", bajty(alfa, "PNG"))["sciezka"].endswith(".webp"))
    pelny = Image.new("RGB", (100, 100), "blue")
    sprawdz("PNG bez przezroczystości -> .jpg", galeria.wgraj("ekran.png", bajty(pelny, "PNG"))["sciezka"].endswith(".jpg"))
    sprawdz("WebP przyjęty", galeria.wgraj("x.webp", bajty(pelny, "WEBP"))["sciezka"].endswith(".jpg"))

    sprawdz("ścieżka w nazwie nie wychodzi z uploads/",
            galeria.wgraj("../../etc/passwd.jpg", bajty(pelny, "JPEG"))["sciezka"] == "uploads/passwd.jpg")
    sprawdz("końcówka -sm nie udaje wariantu",
            galeria.wgraj("wino-sm.jpg", bajty(pelny, "JPEG"))["sciezka"] == "uploads/wino.jpg")

    odrzuca("PDF z rozszerzeniem .jpg odrzucony", lambda: galeria.wgraj("a.jpg", b"%PDF-1.4 nie obraz"))
    odrzuca("GIF odrzucony (tylko JPG/PNG/WebP)", lambda: galeria.wgraj("a.gif", bajty(pelny, "GIF")))
    odrzuca("pusty plik odrzucony", lambda: galeria.wgraj("a.jpg", b""))
    odrzuca("plik ponad limit odrzucony", lambda: galeria.wgraj("a.jpg", b"\xff" * (galeria.MAX_WGRYWANIE + 1)))
    duzy = bajty(Image.new("1", (8000, 7000)), "PNG")
    odrzuca("obraz ponad 50 Mpx odrzucony", lambda: galeria.wgraj("duzy.png", duzy))

    sprawdz("brak plików tymczasowych po wgrywaniu",
            not any(p.name.startswith(".wgrywanie.") for p in galeria.uploads().iterdir()))


def testy_usuwania(zasoby: Path) -> None:
    pelny = bajty(Image.new("RGB", (50, 50), "green"), "JPEG")
    wolny = galeria.wgraj("wolny.jpg", pelny)["sciezka"]
    w_cenniku = galeria.wgraj("butelka.jpg", pelny)["sciezka"]
    w_wydarzeniu = galeria.wgraj("impreza.jpg", pelny)["sciezka"]
    (zasoby / "photos").mkdir(exist_ok=True)
    Image.new("RGB", (10, 10)).save(zasoby / "photos" / "hero.jpg")

    Path(os.environ["CENNIK_SCIEZKA"]).write_text(json.dumps({"wina": [
        {"id": "monarch-2022", "nazwa": "Monarch", "zdjecie_sklep": f"./attached_assets/{w_cenniku}"}]}))
    Path(os.environ["WYDARZENIA_SCIEZKA"]).write_text(json.dumps({"wydarzenia": [
        {"id": "x", "tytul": "Impreza", "zdjecia": [w_wydarzeniu]}]}))
    uzycia = galeria.uzycia_zdjec()
    sprawdz("użycie w cenniku rozpoznane mimo prefiksu ./attached_assets/",
            uzycia.get(w_cenniku) == ["cennik: Monarch (monarch-2022)"])
    sprawdz("użycie w wydarzeniu rozpoznane", uzycia.get(w_wydarzeniu) == ["wydarzenie: Impreza"])

    try:
        galeria.usun([wolny, w_cenniku], uzycia)
    except galeria.PlikUzywany as blad:
        sprawdz("używany plik blokuje usuwanie i jest wskazany", list(blad.uzycia) == [w_cenniku])
    else:
        sprawdz("używany plik blokuje usuwanie", False)
    sprawdz("wszystko albo nic: wolny plik nadal istnieje", (zasoby / wolny).is_file())

    odrzuca("plik spoza uploads/ nieusuwalny", lambda: galeria.usun(["photos/hero.jpg"], uzycia))
    sprawdz("hero nietknięte", (zasoby / "photos" / "hero.jpg").is_file())
    odrzuca("ścieżka z .. odrzucona", lambda: galeria.usun(["uploads/../photos/hero.jpg"], uzycia))
    odrzuca("nieistniejący plik odrzucony", lambda: galeria.usun(["uploads/brak.jpg"], uzycia))
    odrzuca("duplikat odrzucony", lambda: galeria.usun([wolny, wolny], uzycia))

    sprawdz("wolny plik usunięty", galeria.usun([wolny], uzycia) == 1 and not (zasoby / wolny).exists())


def testy_dowiazania(baza: Path) -> None:
    """Produkcja: attached_assets/uploads -> dane/uploads poza attached_assets."""
    zasoby = baza / "attached_assets"
    (zasoby / "photos").mkdir(parents=True)
    zewnetrzny = baza / "dane" / "uploads"
    zewnetrzny.mkdir(parents=True)
    (zasoby / "uploads").symlink_to(zewnetrzny, target_is_directory=True)
    sekret = baza / "sekret"
    sekret.mkdir()
    Image.new("RGB", (10, 10)).save(sekret / "tajne.jpg")
    (zasoby / "photos" / "wyciek").symlink_to(sekret, target_is_directory=True)
    galeria.ZASOBY = zasoby

    wynik = galeria.wgraj("przez-dowiazanie.jpg", bajty(Image.new("RGB", (20, 20)), "JPEG"))
    sprawdz("dowiązanie: plik fizycznie w dane/uploads", (zewnetrzny / "przez-dowiazanie.jpg").is_file())
    sprawdz("dowiązanie: ścieżka względna nadal uploads/…", wynik["sciezka"] == "uploads/przez-dowiazanie.jpg")
    sciezki = [p["sciezka"] for p in galeria.stan()["pliki"]]
    sprawdz("dowiązanie: galeria listuje plik z uploads/", "uploads/przez-dowiazanie.jpg" in sciezki)
    sprawdz("dowiązanie: inne dowiązanie poza zasoby nie jest listowane", not any("tajne" in s for s in sciezki))
    sprawdz("dowiązanie: w_zasobach przyjmuje uploads/", galeria.w_zasobach(wynik["sciezka"]) is not None)
    sprawdz("dowiązanie: w_zasobach odrzuca obce dowiązanie", galeria.w_zasobach("photos/wyciek/tajne.jpg") is None)
    sprawdz("dowiązanie: cennik przyjmuje zdjecie_sklep z uploads/",
            cennik.sciezka_zdjecia_sklep(f"attached_assets/{wynik['sciezka']}") is not None)
    bledy = wydarzenia.waliduj({"wydarzenia": [{"id": "a", "tytul": "A", "tresc": "B",
                                                "data_od": "2026-01-01", "data_do": "2026-01-02",
                                                "zdjecia": [wynik["sciezka"]]}]})
    sprawdz("dowiązanie: wydarzenia przyjmują zdjecia z uploads/", bledy == [])
    sprawdz("dowiązanie: usuwanie działa", galeria.usun([wynik["sciezka"]], {}) == 1
            and not (zewnetrzny / "przez-dowiazanie.jpg").exists())


def main() -> int:
    poprzednie = galeria.ZASOBY
    try:
        with TemporaryDirectory() as tymczasowy:
            zasoby = Path(tymczasowy) / "attached_assets"
            zasoby.mkdir()
            galeria.ZASOBY = zasoby
            testy_wgrywania(zasoby)
            testy_usuwania(zasoby)
        with TemporaryDirectory() as tymczasowy:
            testy_dowiazania(Path(tymczasowy))
    finally:
        galeria.ZASOBY = poprzednie
        _TMP.cleanup()

    print("\nWSZYSTKIE TESTY PRZESZŁY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
