# Wdrożenie

Aplikacją zarządza `projects_manager` (`/home/vs/repo/ops02/projects_manager`), konfiguracja
projektu: `production_projects/winnicakielnagora.env`.

| | |
|---|---|
| Katalog aplikacji | `/opt/apps/app_winnicakielnagora.pl` |
| Kod (git) | `${APP_DIR}/app` |
| Usługa | `winnicakielnagora`, gunicorn `wsgi:app` na `127.0.0.1:8004` |
| Adres dev | `https://ops02.jdblayer.com/winnicakielnagora.pl/` |
| Strategia nginx | `prefix` — blok doklejany do `moderacja.conf` |

## Stan na 2026-09-02: aplikacja nie działa jako usługa

Sprawdzone na żywo: pod adresem dev pliki są wydawane **z pominięciem Flaska**. Skutki:

- `/.git/config`, `/wsgi.py`, `/cennik.py`, `/TODO.md` → **200** (patrz `TODO.md` #28),
- `/wina/monarch` (ładne adresy) → 404,
- `/tools/panel/api/wczytaj` → 404, więc panel dostaje HTML zamiast danych,
- `/nie-ma-takiej-strony` → domyślna strona Werkzeuga zamiast naszego `404.html`.

Wszystkie zabezpieczenia w `wsgi.py` — lista dozwolonych plików, hasło do panelu, obsługa
404 — **działają dopiero wtedy, gdy ruch przechodzi przez aplikację**. Dopóki nginx serwuje
katalog aliasem, są martwe.

## Co trzeba zrobić

### 1. Sprawdzić blok nginx dla prefiksu

`production_manager.sh` generuje dla `NGINX_STRATEGY=prefix` blok z `proxy_pass`
na `127.0.0.1:8004`. Jeśli w `moderacja.conf` pod `location ^~ /winnicakielnagora.pl/`
jest zamiast tego `alias` albo `root`, ruch nigdy nie trafia do aplikacji — trzeba go
zastąpić blokiem proxy.

Zapasowo, niezależnie od aplikacji, warto zablokować wrażliwe ścieżki na poziomie nginx —
przez `NGINX_LOCATION_EXTRA` albo ręcznie w konfiguracji:

```nginx
location ~ /\.git { deny all; return 404; }
```

### 2. Uzupełnić `winnicakielnagora.env`

Zmienne dla procesu gunicorna przekazuje się przez `EXTRA_SYSTEMD_ENV` (skrypt dzieli je po
spacjach i zamienia na `Environment=` w unicie systemd, więc **żadna wartość nie może zawierać
spacji**).

```bash
EXTRA_SYSTEMD_ENV='CENNIK_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wina.json PANEL_UZYTKOWNIK=wlasciciel PANEL_HASLO_HASH=<z tools/panel/haslo.py>'
```

Uwagi:

- **Apostrofy, nie cudzysłowy.** Hash zawiera dwukropek i szesnastkowe znaki, ale plik `.env`
  czyta bash — apostrofy chronią przed niespodziankami przy każdej przyszłej wartości.
- `CENNIK_SCIEZKA` wskazuje **poza** `${APP_DIR}/app`, czyli poza katalog z gitem. Dzięki temu
  wdrożenie nie kasuje cen wpisanych panelem (`TODO.md` #26). Katalog `dane/` trzeba utworzyć
  i nadać prawo zapisu użytkownikowi `winnicakielnagora`:

  ```bash
  sudo -u winnicakielnagora mkdir -p /opt/apps/app_winnicakielnagora.pl/dane
  ```

- Hash generuje `python3 tools/panel/haslo.py`. **Hasła nie zapisuj nigdzie** — do konfiguracji
  trafia wyłącznie hash.
- Bez `PANEL_UZYTKOWNIK` i `PANEL_HASLO_HASH` panel na produkcji nie istnieje (404). To celowe.

### 3. Uruchomić usługę

```bash
cd /home/vs/repo/ops02/projects_manager
sudo ./production_manager.sh setup winnicakielnagora     # pierwsze uruchomienie
sudo ./production_manager.sh update winnicakielnagora    # kolejne wdrożenia
sudo ./production_manager.sh restart winnicakielnagora
sudo ./production_manager.sh status winnicakielnagora
sudo ./production_manager.sh logs winnicakielnagora 200
```

Projekt nie ma kroku budowania — `BUILD_CMD` ma zostać zakomentowany.

### 4. Sprawdzić po wdrożeniu

```bash
B=https://ops02.jdblayer.com/winnicakielnagora.pl
curl -s -o /dev/null -w "%{http_code}\n" $B/            # 200
curl -s -o /dev/null -w "%{http_code}\n" $B/wina/monarch # 200 (ładne adresy)
curl -s -o /dev/null -w "%{http_code}\n" $B/nie-ma       # 404 (nasza strona błędu)
curl -s -o /dev/null -w "%{http_code}\n" $B/wsgi.py      # 404
curl -s -o /dev/null -w "%{http_code}\n" $B/.git/config  # 404
curl -s -o /dev/null -w "%{http_code}\n" $B/tools/panel/api/wczytaj  # 401
```

Ostatnie żądanie ma zwrócić **401**, a nie 404 — 404 znaczy, że zmienne panelu nie doszły
do procesu.

## Podścieżka

Nginx przekazuje pełny adres razem z prefiksem, a `SET_SCRIPT_NAME` (domyślnie `1`) ustawia
`SCRIPT_NAME=/winnicakielnagora.pl` w unicie — gunicorn sam obcina prefiks i Flask widzi
ścieżki od korzenia.

Gdyby ta droga zawiodła, `wsgi.py` ma warstwę `ObetnijPrzedrostek`: ustaw
`SCIEZKA_BAZOWA=winnicakielnagora.pl` w `EXTRA_SYSTEMD_ENV`, a przedrostek zostanie obcięty
w aplikacji. Obie drogi da się włączyć naraz — warstwa nic nie zrobi, jeśli prefiks już
został obcięty.

## Czego wdrożenie nie dotyka

- `dane/wina.json` — żywy cennik, poza katalogiem z gitem (patrz wyżej).
- `data/wina.json` w repozytorium — **wersja startowa**, kopiowana tylko wtedy, gdy pliku
  roboczego jeszcze nie ma.
- `docs/` i zrzuty z `audit/` — nie są w repozytorium (`.gitignore`).
