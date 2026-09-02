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
EXTRA_SYSTEMD_ENV='PYTHONDONTWRITEBYTECODE=1 CENNIK_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wina.json PANEL_UZYTKOWNIK=wlasciciel PANEL_HASLO_HASH=<z tools/panel/haslo.py>'
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

### 4. Sprawdzić, czy działa TEN kod

Najszybszy test — punkt kontrolny `/zdrowie` zwraca skrót z `wsgi.py` i `cennik.py`:

```bash
curl -s https://ops02.jdblayer.com/winnicakielnagora.pl/zdrowie
python3 -c "import hashlib,pathlib; print(hashlib.sha256(b''.join(pathlib.Path(p).read_bytes() for p in ('wsgi.py','cennik.py'))).hexdigest()[:12])"
```

Te dwie wartości muszą być identyczne. Jeśli `/zdrowie` zwraca 404 albo stronę HTML,
**proces nie wykonuje tego kodu** — patrz „Gdy `/zdrowie` nie odpowiada" niżej.

Odpowiedź mówi też, czy panel jest włączony (`panel_wlaczony`) i skąd czytany jest cennik.

### 5. Sprawdzić po wdrożeniu

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

## Gdy `/zdrowie` nie odpowiada albo znacznik się nie zgadza

Objaw z 2026-09-02: `wsgi.py` na dysku serwera był **bajt w bajt identyczny** z repozytorium,
usługa `winnicakielnagora` działała, a mimo to `/wsgi.py` zwracało 200 z nagłówkiem
`content-disposition` (czyli Flaskowym `send_file`), `/wina/monarch` dawało 404 Werkzeuga,
a `/data/wina.json` przychodziło z `cache-control: no-cache` zamiast naszego `no-store`.

To znaczy, że żądania obsługuje **inny proces niż nasz** albo nasz proces trzyma starszy kod.
Do sprawdzenia, w tej kolejności:

> **Uwaga przy odpytywaniu gunicorna wprost.** Unit ustawia `SCRIPT_NAME=/winnicakielnagora.pl`,
> a gunicorn **odrzuca** każde żądanie, którego ścieżka nie zaczyna się od tego przedrostka —
> zwraca wtedy „Configuration problem: Request path … does not start with SCRIPT_NAME". To nie
> jest usterka aplikacji. Odpytując port 8004 bezpośrednio, **zawsze dopisuj prefiks**.

```bash
# 1. z jakiego katalogu i czym startuje usluga (+ czy dostala zmienne panelu)
systemctl show winnicakielnagora -p WorkingDirectory -p ExecStart -p Environment

# 2. czy gunicorn na 8004 odpowiada poprawnie Z POMINIECIEM nginx
#    UWAGA: z prefiksem, patrz ramka wyzej
P=http://127.0.0.1:8004/winnicakielnagora.pl
curl -s $P/zdrowie                                            # znacznik kodu
curl -s -o /dev/null -w "%{http_code}\n" $P/wsgi.py          # ma byc 404
curl -s -o /dev/null -w "%{http_code}\n" $P/.git/config      # ma byc 404

# 3. dokad nginx kieruje ten prefiks — proxy_pass czy alias/root?
grep -n -B2 -A14 "winnicakielnagora" /etc/nginx/sites-available/moderacja.conf

# 4. stary bytecode albo druga kopia kodu
ls -la /opt/apps/app_winnicakielnagora.pl/app/__pycache__
find /opt/apps/app_winnicakielnagora.pl -maxdepth 2 -name "wsgi.py"
```

Interpretacja:

- **Punkt 2 działa poprawnie, a przez nginx nie** → nginx nie kieruje ruchu do naszej usługi;
  w bloku prefiksu jest `alias`/`root` zamiast `proxy_pass`, albo prefiks przejmuje wcześniejszy
  blok innej aplikacji z `moderacja.conf`.
- **Punkt 2 też zwraca 200 dla `/wsgi.py`** → proces trzyma stary kod. Patrz niżej.
- **Znajdzie się druga kopia `wsgi.py`** (np. w `${APP_DIR}` obok `${APP_DIR}/app`) → gunicorn
  importuje tamtą; `WorkingDirectory` musi wskazywać katalog z repozytorium.

### Osierocony proces trzymający port 8004

Objaw: plik na dysku jest aktualny, `__pycache__` usunięty, `systemctl status` pokazuje
„active (running)", a mimo to aplikacja zachowuje się jak sprzed kilku wdrożeń.

**To się wydarzyło 2026-09-02.** Port trzymały procesy z poprzedniego dnia:

```
LISTEN 127.0.0.1:8004  users:(("python",pid=964),("python",pid=958),("python",pid=957),("python",pid=666))
    666  Tue Sep  1 15:17:33  ...--bind 127.0.0.1:8004 wsgi:app            <- stary, trzyma port
 218135  Wed Sep  2 22:21:41  ...--bind 127.0.0.1:8004 --timeout 300 wsgi:app   <- nowy, bez portu
```

Rozpoznaje się to po **czasie startu** i po linii poleceń: unit dodaje `--timeout 300`,
więc proces bez tego argumentu pochodzi sprzed zmiany konfiguracji.

Przyczyna: **stary gunicorn nadal zajmuje port 8004**. Nowa usługa nie może się podpiąć,
kończy się błędem „Address already in use" i wpada w pętlę restartów — `status` złapany
zaraz po starcie zdąży jeszcze pokazać „running".

```bash
# kto naprawde trzyma port
sudo ss -ltnp | grep 8004
ps -eo pid,lstart,cmd | grep -i "[g]unicorn"     # zwroc uwage na czas startu procesu

# czy usluga sie nie restartuje w kolko
sudo systemctl status winnicakielnagora --no-pager
sudo journalctl -u winnicakielnagora -n 50 --no-pager | grep -i "address already in use\|Traceback\|error"
```

Naprawa — najpierw ustal, czy stary proces nie należy do innego unitu, bo wtedy systemd
wskrzesi go natychmiast:

```bash
cat /proc/666/cgroup                    # nazwa unitu albo brak przynaleznosci
ps -o pid,ppid,lstart,cmd -p 666
```

Jeśli to sierota (`ppid=1`, cgroup bez unitu aplikacji):

```bash
sudo systemctl stop winnicakielnagora
sudo kill 666                           # master; workery zgina razem z nim
sleep 2 && sudo ss -ltnp | grep 8004    # ma byc pusto
sudo systemctl start winnicakielnagora
curl -s http://127.0.0.1:8004/winnicakielnagora.pl/zdrowie
```

Jeśli `cgroup` wskaże **inny unit** — to on uruchamia tę aplikację równolegle i trzeba go
wyłączyć (`sudo systemctl disable --now <unit>`), inaczej problem wróci po restarcie maszyny.
Stare procesy wystartowały o tej samej sekundzie co kilkanaście innych aplikacji, co wygląda
na wspólny start przy bootowaniu — warto sprawdzić, czy nie ma drugiego mechanizmu
uruchamiania (stary unit, `@reboot` w cronie, supervisor).

Jeśli w logu jest `Traceback` zamiast błędu portu — aplikacja nie startuje z innego powodu
i trzeba przeczytać wyjątek.

### Stary bytecode — znany, konkretny przypadek

Plik `__pycache__/wsgi.cpython-311.pyc` był przez pomyłkę **śledzony w repozytorium** od
pierwszych commitów aż do `09178bc`. Serwery, które pobrały kod wcześniej, dostały skompilowaną
starą wersję modułu razem ze źródłem.

```bash
sudo rm -rf /opt/apps/app_winnicakielnagora.pl/app/__pycache__
sudo systemctl restart winnicakielnagora
curl -s http://127.0.0.1:8004/winnicakielnagora.pl/zdrowie
```

Żeby to nie wróciło, warto dopisać do `EXTRA_SYSTEMD_ENV`:

```
PYTHONDONTWRITEBYTECODE=1
```

Wtedy proces w ogóle nie tworzy `__pycache__`, kosztem paru milisekund przy starcie.

