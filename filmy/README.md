# Filmy

Skompresowane wersje webowe filmów z winnicy. Oryginały (12 plików 1080p, 6–74 MB) leżą
w `docs/materialy-do-wykorzystania/`, który jest w `.gitignore`.

Ten katalog jest **serwowany publicznie** — jest na liście `KATALOGI_PUBLICZNE` w `wsgi.py`.

Kompresja (ffmpeg jest zainstalowany):

```bash
ffmpeg -i "docs/materialy-do-wykorzystania/Monarch/20250922_143511.mp4" \
  -vf "scale=1280:-2" -c:v libx264 -crf 28 -preset slow -an \
  -movflags +faststart filmy/monarch-zbiory.mp4
```

`-an` usuwa ścieżkę dźwiękową (filmy w tle i tak są wyciszone), `+faststart` pozwala
przeglądarce zacząć odtwarzanie przed pobraniem całości.

Patrz `TODO.md` #16 — nie ma jeszcze decyzji, czy i gdzie filmy trafią na stronę.
