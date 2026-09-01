# AGENTS.md - app_winnicakielnagora.pl

**Wersja: 1.0.0** (2026-09-01) - pierwsza wersja, napisana z odczytu drzewa, `wsgi.py`
i konfiguracji wdrozeniowej `projects_manager/production_projects/winnicakielnagora.env`.

## Czym jest ten plik

**Obowiazuje kazdego asystenta AI pracujacego w tym katalogu. Przeczytaj go na starcie sesji.**

- **Zakres: tylko ten projekt.** Reguly wspolne dla calego jdblayera sa w
  `/home/vs/repo/AGENTS.md` i nie sa tu powtarzane.
- To instrukcja JAK pracowac, nie zapis CO zrobiono.

## Co to jest

Statyczna witryna winnicy - jedna strona `index.html` (~58 KB) plus `assets/`
i `attached_assets/`. Nie ma tu backendu, bazy, testow ani zaleznosci.

Calosc serwera to 14 linii w `wsgi.py`: Flask oddaje pliki z `dist/public`, jesli ten katalog
istnieje, a w przeciwnym razie wprost z katalogu repozytorium, z fallbackiem na `index.html`
dla kazdej nieznanej sciezki.

- Produkcja: gunicorn `wsgi:app` na `127.0.0.1:8004`, domena `ops02.jdblayer.com`,
  katalog `/opt/apps/app_winnicakielnagora.pl`, `python3.11`. Wdraza `projects_manager`.
- **Krok budowania nie jest ustawiony** w konfiguracji wdrozeniowej, wiec katalog
  `dist/public` na produkcji nie powstaje sam. Zanim oprzesz cokolwiek na tej galezi
  w `wsgi.py`, ustal z Wlascicielem, czy build ma byc dodany.

## Zasady pracy

1. **Sprawdz `git status` przed pierwsza edycja.** Repozytorium bywa zostawiane
   z niezacommitowana praca (edycje `index.html`, nowe pliki w
   `attached_assets/generated_images/`). To czyjas praca w toku - nie nadpisuj jej
   i nie commituj razem ze swoja zmiana.
2. **`index.html` jest jednym wielkim plikiem.** Zmieniaj w nim dokladnie ten fragment,
   ktorego dotyczy zadanie; nie przeformatowuj calosci i nie "porzadkuj" znacznikow przy
   okazji - diff staje sie wtedy nieczytelny, a to jedyna kopia tresci strony.
3. **Zmiana wygladu nie ma tu zadnego testu.** Jedyna weryfikacja to podglad strony,
   wiec opisz w odpowiedzi, co konkretnie sprawdzic i gdzie.
4. **Obrazy trzymaj w `assets/` albo `attached_assets/`** i wstawiaj sciezkami wzglednymi -
   `wsgi.py` serwuje katalog repozytorium jako statyczny root.
5. Nie dodawaj zaleznosci Pythona bez potrzeby. Ten projekt celowo nie ma
   `requirements.txt` - jedynym wymaganiem srodowiska jest Flask i gunicorn.

## Czego nie ustalono

- Czy istnieje zrodlo, z ktorego `index.html` jest generowany (np. projekt front-endowy
  poza tym repozytorium). Jesli tak, edycja `index.html` wprost bedzie nadpisana przy
  nastepnym buildzie - **sprawdz, zanim zaczniesz wieksza zmiane**.
