# Panel redakcyjny cennika

Edytuje `data/wina.json` — jedyne źródło asortymentu i cen w sklepie.

```bash
python3 tools/panel/serwer.py            # → http://127.0.0.1:8765
python3 tools/panel/serwer.py --port 9000
```

Zatrzymanie: `Ctrl+C`. Panel nie wymaga instalowania niczego — działa na samym Pythonie.

## Czego panel nie robi

- **Nie publikuje.** Po zapisie zmiany są tylko na dysku. Trzeba zrobić commit i wdrożenie.
- **Nie edytuje stron odmian** (`wina/*.html`), sekcji „O nas", kontaktu ani wydarzeń.
- **Nie wgrywa zdjęć.** Wybiera spośród plików w `attached_assets/photos/`. Nowe zdjęcia
  dokłada `python3 tools/optimize-photos.py`.

## Panel na produkcji (za hasłem)

Ten sam interfejs działa pod `https://winnicakielnagora.pl/tools/panel/panel.html`, obsługiwany
przez `wsgi.py`. **Włącza się wyłącznie**, gdy w konfiguracji wdrożeniowej są obie zmienne:

```bash
python3 tools/panel/haslo.py     # wypisze obie linijki do wklejenia
```

```
PANEL_UZYTKOWNIK=...
PANEL_HASLO_HASH=...
```

Bez nich każde `/tools/panel/…` zwraca **404** — nie 401 — więc brak konfiguracji nie zdradza,
że cokolwiek tam jest. Hasło i jego hash nigdy nie trafiają do repozytorium.

Do tego trzecia zmienna, żeby wdrożenie nie kasowało cen wpisanych przez panel:

```
CENNIK_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wina.json
```

Katalog `dane/` ma leżeć **poza** tym, co wdrożenie synchronizuje z repozytorium, i mieć prawo
zapisu dla użytkownika gunicorna. Przy pierwszym żądaniu aplikacja skopiuje tam wersję startową
z `data/wina.json`; potem plik żyje własnym życiem i żaden deploy go nie tknie.

Od tej chwili `data/wina.json` w repozytorium to **wersja startowa, nie produkcyjna**. Żeby
zgrać ceny z serwera z powrotem do gita, skopiuj plik ręcznie.

**Zanim to włączysz, przeczytaj `TODO.md` #26 i #27:**

- Basic Auth wysyła hasło przy każdym żądaniu, więc panel wymaga **HTTPS**.
- Zmiana zrobiona na produkcji **nie jest w gicie** i może przepaść przy następnym wdrożeniu.

## Bezpieczeństwo wariantu lokalnego

Lokalny `serwer.py` **nie ma logowania**, dlatego nasłuchuje wyłącznie na `127.0.0.1`,
sprawdza adres klienta przy każdym żądaniu i wymaga nagłówka `Origin` przy zapisie.

**Nigdy nie uruchamiaj go na `0.0.0.0` i nie wdrażaj tego pliku.**

Przed każdym zapisem powstaje kopia `data/wina.json.bak` (jest w `.gitignore`), a sam zapis
jest atomowy — przerwanie w połowie nie zostawi uszkodzonego pliku.

## Pomoc w opisie (opcjonalna)

Pole „Pomoc w opisie" wysyła wklejone notatki do OpenAI i dostaje z nich dwa teksty: krótki
opis na kartę produktu oraz opis meta do strony odmiany. Bez klucza API panel działa normalnie —
po prostu ta jedna funkcja wyświetla komunikat.

```bash
export OPENAI_API_KEY=sk-...
python3 tools/panel/serwer.py
```

| Zmienna | Domyślnie | Do czego |
|---|---|---|
| `OPENAI_API_KEY` | — | wymagana do tej funkcji; **nigdy nie wpisuj jej do plików w repo** |
| `OPENAI_MODEL` | `gpt-4o-mini` | nazwy modeli się zmieniają — podmienisz bez ruszania kodu |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | inny endpoint zgodny z API OpenAI |

Uwagi:

- **Wklejona treść opuszcza infrastrukturę** i trafia do OpenAI. Dla notatek o winie to bez
  znaczenia, ale nie wklejaj tam danych osobowych — nazwisk klientów, adresów, treści maili.
- Model dostaje zakaz dodawania faktów spoza wklejonego tekstu, ale **to nie jest gwarancja** —
  przeczytaj propozycję, zanim ją wstawisz.
- Nic nie zapisuje się samo. Propozycja ląduje w polu formularza dopiero po kliknięciu
  „Wstaw do pola", a plik zmienia się dopiero po „Zapisz".
- Wejście jest ograniczone do 20 000 znaków, żeby jedno kliknięcie nie wygenerowało rachunku.
