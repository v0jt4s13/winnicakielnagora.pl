# winnicakielnagora.pl — szybki start

```bash
git clone git@github.com:v0jt4s13/winnicakielnagora.pl.git
````

```bash
# Dev server (bez SMTP, wystarcza do przeglądania strony)
python3 tools/dev-server.py --port 5000
# → http://localhost:5000

# Wariant produkcyjny (Flask/gunicorn)
python3 -m flask --app wsgi run --port 8004

# Testy
python3 tools/test-contact.py
python3 tools/test-cennik-sciezka.py
python3 tools/test-galeria.py
python3 tools/test-panel-auth.py
python3 tools/test-routing.py
python3 tools/test-serwowanie.py
python3 tools/test-wydarzenia.py

# Panel redakcyjny (lokalnie, bez hasła)
python3 tools/panel/serwer.py
```
