# fetch() w panel.js zawsze względny, nigdy od `/`

Na produkcji panel jest za nginx z prefiksem `/winnicakielnagora.pl/` (patrz
`X-Script-Name`/`X-Forwarded-Prefix` w konfiguracji nginx — poza repo). Ścieżka
zaczynająca się od `/` pomija ten prefiks i trafia do korzenia domeny, gdzie nginx
nie ma dla niej żadnej reguły → **404, mimo że endpoint istnieje i działa poprawnie
w Flasku** (wypadek 2026-09-22: `o-nas-galeria-dodaj-z-galerii` zwracał 404 tylko
na produkcji, lokalnie działał).

```js
// źle — pomija prefiks nginx na produkcji
fetch("/tools/panel/api/o-nas-galeria-dodaj-z-galerii", { ... });

// dobrze — dziedziczy prefiks z aktualnego URL-a panelu
fetch("api/o-nas-galeria-dodaj-z-galerii", { ... });
```

Cały pozostały kod w `panel.js` już używa względnych ścieżek (`fetch("api/wczytaj")`
itd.) — to jedyny wyjątek, jaki się zdarzył.

## Jak to sprawdzić przy debugowaniu podobnego 404

1. Endpoint działa lokalnie, ale 404 tylko na produkcji → podejrzewaj prefiks, nie kod Pythona.
2. W DevTools → Network → nagłówek odpowiedzi `server`: `nginx` znaczy, że żądanie
   nie dotarło do Flaska (nginx odciął je wcześniej); `gunicorn` znaczy, że dotarło.
3. `curl` bezpośrednio na `127.0.0.1:8004` (port gunicorna) pomija nginx — jeśli
   tam endpoint działa (nawet z 401/400), problem jest w konfiguracji nginx albo
   w tym, jak JS buduje URL, nie w `wsgi.py`.

## Why

Lokalny dev-server (`tools/panel/serwer.py`) nie ma prefiksu — bezwzględna ścieżka
działa tam bez zarzutu, więc błąd jest niewidoczny do czasu wdrożenia na produkcję.
