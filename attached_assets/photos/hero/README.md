# Kadry zdjecia wejsciowego (hero)

Cztery kadry pory dnia: `poranek`, `dzien`, `zachod`, `noc`. Uzywaja ich `index.html`
i `404.html`; kadr dla strony glownej wybiera serwer (`wsgi.py`, patrz SPEC-003).

## Co tu lezy, a czego nie

W repozytorium sa **wylacznie `*.webp`** — to one ida do przegladarki.

Mastery (PNG, ok. 2 MB kazdy) leza **poza repozytorium**, w
`docs/materialy-do-wykorzystania/hero/`. Katalog `docs/` jest w `.gitignore`, tak samo jak
material zrodlowy dla `tools/optimize-photos.py`. Wczesniej kopie PNG lezaly rowniez tutaj
i jechaly na wdrozenie (8,2 MB), mimo ze zadna strona ich nie wczytywala — zostaly usuniete.

Konsekwencja: **swiezy klon nie ma z czego przekodowac kadrow.** Potrzebne sa oryginaly
od Wlasciciela. To swiadome — repozytorium nie jest magazynem materialu zrodlowego.

## Podmiana kadru

1. Wrzuc nowy PNG do `docs/materialy-do-wykorzystania/hero/` pod ta sama nazwa
   (`poranek` / `dzien` / `zachod` / `noc`).
2. Zachowaj **1534x1025**. Inny rozmiar zmieni kadrowanie i wywola przeskok ukladu —
   `width` i `height` sa zaszyte w `index.html` i `404.html`.
3. `python3 tools/optimize-hero.py` — nadpisze `*.webp` w tym katalogu (q80).
4. Obejrzyj strone glowna we wszystkich trzech motywach; nocny kadr wlacza ciemny `modern`.

## Czego nie robic

Nie przepinaj sciezek w HTML-u z powrotem na PNG. Kadr hero jest elementem LCP strony
glownej — plik po 2 MB kasuje caly zysk z preloadu wstawianego przez serwer.
