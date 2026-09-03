# Kadry zdjecia wejsciowego (hero)

## Co jest czym

| Plik | Rola |
|---|---|
| `*.webp` | to, co dostaje przegladarka — jedyne pliki uzywane przez `index.html` i `404.html` |
| `*.png` | master, z ktorego powstal WebP; **nic ich juz nie wczytuje** |

WebP powstaje z PNG przez `python3 tools/optimize-hero.py` (q80, bez zmiany rozdzielczosci).

## Notka dla designera — do decyzji

Cztery PNG waza razem **8,2 MB** i leza w katalogu publicznym, wiec jada na wdrozenie,
mimo ze zadna strona ich nie wczytuje. Zostawilismy je celowo, bo to material zrodlowy,
a nie nasza decyzja, czy jest jeszcze potrzebny.

**Jesli sa zbedne** — usun je albo przenies do `docs/materialy-do-wykorzystania/hero/`
(ten katalog nie jest serwowany, patrz `KATALOGI_PUBLICZNE` w `wsgi.py`). Same PNG-i nie
sa potrzebne do dzialania strony; potrzebne sa tylko wtedy, gdy ktos bedzie chcial
przekodowac kadry ponownie w innej jakosci.

**Jesli zostaja** — nie usuwaj `*.webp` i nie podmieniaj sciezek w HTML-u z powrotem na PNG:
kadr hero jest elementem LCP strony glownej, a PNG po ok. 2 MB psuje czas ladowania.

## Podmiana kadru

1. Wrzuc nowy PNG pod ta sama nazwa (`poranek` / `dzien` / `zachod` / `noc`).
2. Zachowaj **1534x1025** — inny rozmiar zmieni kadrowanie i wywola przeskok ukladu
   (`width`/`height` sa zaszyte w `index.html` i `404.html`).
3. Uruchom `python3 tools/optimize-hero.py`.
