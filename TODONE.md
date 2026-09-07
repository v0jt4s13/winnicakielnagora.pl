# TODONE — zamknięte pozycje

Archiwum spraw z `TODO.md`, które zostały domknięte. Trzymamy je z datami i krótkim
opisem rozwiązania, żeby nie wracać do już podjętych decyzji i żeby odwołania w kodzie
(`TODO.md #N`) dalej miały pokrycie. Sprawy wciąż otwarte są w `TODO.md`; sklepowe
i zawieszone — w `TODO.maybefuture.md`.

Ostatnia aktualizacja: **2026-09-07**.

## Rozjazdy w kodzie

### 1. Rozjazd ceny netto — ZAMKNIĘTE 2026-09-02

Atrapy produktów usunięte, netto jest wyliczane z `cena_brutto`.

### 2. Filtr cenowy ma zaszyty zakres 0–100 zł — ZAMKNIĘTE 2026-09-02

Zakres liczy `zakresCen()` z cen w `data/wina.json`.

### 3. Martwe atrybuty `data-price-net` i `data-discount` — ZAMKNIĘTE 2026-09-02

Karty renderuje `Produkty.renderProductCard()`; oba atrybuty zniknęły.

### 4. VAT 23% zaszyty w dwóch miejscach — ZAMKNIĘTE 2026-09-02

Stawka pochodzi z `data/wina.json`, etykieta koszyka budowana jest z niej (`#cart-tax-label`).

### 5. `wsgi.py` nigdy nie zwraca 404 — ZAMKNIĘTE 2026-09-02

Nieznany adres zwraca `404.html` z kodem 404. Przy okazji zawężono zbiór serwowanych plików
i dodano obsługę adresów bez `.html`.

**Uwaga na przyszłość:** `wsgi.py` ma teraz listę `KATALOGI_PUBLICZNE`. Nowy katalog, który
ma być widoczny publicznie (np. `filmy/`), trzeba do niej dopisać — inaczej zwróci 404.

### 6. Rozjazd treści: odmiany vs. produkty w sklepie — ZAMKNIĘTE 2026-09-02

Zmyślone produkty usunięte. Sklep buduje się z `data/wina.json`.

### 11. Adresy stron odmian bez `.html` — ZAMKNIĘTE 2026-09-02

Na produkcji `/wina/monarch` działa tak samo jak `/wina/monarch.html`. Linki w HTML-u zostają
z rozszerzeniem, bo `python3 -m http.server` używany lokalnie tej sztuczki nie zna — a `canonical`
i tak wskazuje wariant z `.html`, więc nie ma duplikatu dla wyszukiwarek.

### 21. Kategorie Dornfeldera i Monarcha — ZAMKNIĘTE 2026-09-03

Poprawione przez Właściciela w panelu. Na produkcji: Dornfelder, Monarch i Swenson Red
mają „Czerwone", pozostałe cztery odmiany „Białe" — 3 czerwone i 4 białe.

Do potwierdzenia drobiazg: Właściciel napisał „4 czerwone i 3 białe", co jest odwrotnością
stanu w danych. Jeśli któreś wino ma się jeszcze przenieść — poprawka zajmuje chwilę w panelu.

### 25 (część). Wnioski z audytu projektanta — ZAMYKANE etapami

Pełny raport: `audit/2026-09-02-homepage/AUDIT.md`. Domknięte:

- Nazwa marki, `WebSite` JSON-LD, metadane Open Graph (2026-09-02).
- **Nawigacja i CTA jako `<a href="#sekcja">`, nie `<button data-scroll>`** — ZAMKNIĘTE 2026-09-07.
  Nawigacja desktop/mobile, CTA w hero, „Napisz do nas" i linki w stopce to linki;
  `data-scroll` został jako marker płynnego przewijania (`initNavigation`).
- **Nagłówek stron odmian na telefonie** (przyciski różnej wysokości, „Nasze odmiany"
  łamane na dwa wiersze) — ZAMKNIĘTE 2026-09-07. Marka `text-lg` + `truncate`, link
  `whitespace-nowrap shrink-0`, `.btn-ghost` z `display:inline-flex`.
- **`Organization` w JSON-LD** — ZAMKNIĘTE 2026-09-07. Blok `["Organization","Winery"]`
  z adresem, telefonem, e-mailem i logo; blokadą był brak danych kontaktowych (poz. #9).
- Pozycja „Degustacje/Wydarzenia prowadzą do tej samej sekcji" — nieaktualna: w menu nie
  ma już „Degustacji" (SPEC-006).

Otwarte bullety audytu zostają w `TODO.md` #25.

## Sprzedaż online i treść

### 10. Asortyment i cennik — ZAMKNIĘTE 2026-09-03

Właściciel wprowadził cennik panelem: 7 win (3 czerwone, 4 białe) i sok winogronowy.
Dane żyją na produkcji w `/opt/apps/app_winnicakielnagora.pl/dane/wina.json`; w repozytorium
`data/wina.json` jest wersją startową (patrz `TODO.maybefuture.md` #34 oraz #26 niżej).

### 12. Svenson Red — ZAMKNIĘTE 2026-09-02

Właściciel potwierdził, że wino z tej odmiany jest produkowane. Strona odmiany powstała.

### 13. Wydarzenia i degustacje — ZAMKNIĘTE 2026-09-06 (SPEC-006)

**Decyzja Właściciela:** degustacji nie oferujemy (na razie). Wszystkie wzmianki zdjęte
z treści — nagłówek sekcji to „Wydarzenia", statyczną kartę zastąpiła „Co się u nas dzieje".
Kalendarz konkretnych wydarzeń prowadzi panel redakcyjny (SPEC-005). Szczegóły:
`.ai/specs/SPEC-006-2026-09-06-strona-bez-sklepu-noclegi.md`.

### 23. Sklep obiecuje dostawę, której nie ma — ZAMKNIĘTE 2026-09-06 (SPEC-006)

**Decyzja Właściciela:** sprzedaż online nie rusza na start (brak logistyki). Sekcja `#sklep`
i koszyk są ukryte (`hidden` + flaga `SKLEP_WLACZONY = false`) — kod i `data/wina.json`
zostają, gotowe do przywrócenia (`TODO.maybefuture.md` #38). Wzmianka o „dostawie do domu"
zeszła z widoku razem z sekcją. Ogólnikowe hasła („Odkryj naszą kolekcję…", hero „Odkryj
wyjątkowy smak…") — do przepisania przy pracach nad treścią (Właściciel).

### 9 (część). Mapa i `Organization` w JSON-LD — ZAMKNIĘTE 2026-09-07

Zmyślone dane kontaktowe usunięto 2026-09-02; adres (Kielnarowa 303, 36-020 Tyczyn),
telefon i e-mail dodano 2026-09-06 (`bfce26f`). Na tej podstawie 2026-09-07:

- w sekcji `#kontakt` pod zdjęciem winnicy jest link „Zobacz na mapie Google" (Google Maps
  URLs API, bez iframe i bez zmyślonego `pb=` — decyzja Właściciela);
- dodano blok `Organization`/`Winery` w JSON-LD (adres, telefon, e-mail, logo).

Pozostała część #9 (NIP i dane do faktury — tylko jeśli rusza sprzedaż) → `TODO.maybefuture.md`.

## Higiena repo i infrastruktura

### 18. Przegląd strony w przeglądarce — WYKONANY 2026-09-02

Sprawdzone: strona główna i strona odmiany w motywach `classic`, `modern` i `rustic`, sklep
renderowany z cennika, zakres filtra policzony z danych, opcje kategorii z JSON-a, dodanie
do koszyka, etykieta VAT, blok „Wina z tej odmiany", konsola bez błędów.

**Przegląd od razu wykrył błąd**, którego testy nie widziały: `fetch("./data/wina.json")`
działał na stronie głównej, ale na `/wina/*.html` szukał `/wina/data/wina.json` i cicho
wpadał w tekst zastępczy. Naprawione — ścieżki liczą się teraz z adresu `main.js`.

Zostało do obejrzenia: układ na telefonie (osobno domykane w `TODO.md` #25).

### 26. Zmiany cennika na produkcji vs. git — ROZSTRZYGNIĘTE 2026-09-02

**Wariant A: wdrożenie pomija `data/`.** Żywy cennik mieszka poza katalogiem aplikacji,
a `data/wina.json` w repozytorium jest wersją startową.

Do ustawienia w konfiguracji wdrożeniowej:

```
CENNIK_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wina.json
WYDARZENIA_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wydarzenia.json
```

`WYDARZENIA_SCIEZKA` działa tak samo i z tego samego powodu (SPEC-005). **Bez niej wpisy
wydarzeń zrobione panelem znikną przy najbliższym wdrożeniu.**

Plus po stronie serwera: katalog `dane/` poza katalogiem synchronizowanym z repozytorium,
z prawem zapisu dla użytkownika gunicorna; wdrożenie ma pomijać `data/`. Przy pierwszym
żądaniu `zapewnij_plik()` kopiuje wersję z repozytorium na ścieżkę roboczą; kolejne
wdrożenia jej nie ruszają. Sprawdza to `tools/test-cennik-sciezka.py`.

**Konsekwencja:** `data/wina.json` w repozytorium przestaje odzwierciedlać produkcję —
traktuj go jak wersję startową (zgranie z powrotem: `TODO.maybefuture.md` #34).

### 28. Katalog `.git` publicznie dostępny — ZAMKNIĘTE 2026-09-02

Po naprawie #29 ruch przechodzi przez aplikację i lista dozwolonych plików działa.
Sprawdzone na żywo: `/.git/config`, `/wsgi.py`, `/cennik.py`, `/WDROZENIE.md` → **404**.

Warto mimo to dołożyć `location ~ /\.git { deny all; return 404; }` w nginx — wtedy ochrona
nie zależy od tego, czy aplikacja działa.

### 29. Aplikacja nie wykonywała aktualnego kodu — ZAMKNIĘTE 2026-09-02

**Przyczyna: dwie usługi systemd dla tej samej aplikacji.** Port 8004 trzymał gunicorn
należący do unitu `winnicakielnagora.pl.service` (z `.pl`), a `projects_manager` zarządza
unitem `winnicakielnagora.service` (bez `.pl`). Naprawione zatrzymaniem starego procesu.
Domknięcie trwałe: #32.

### 30. Uruchamianie lokalnego serwera panelu z przeglądarki — ODRZUCONE 2026-09-02

Pomysł: przycisk w panelu startujący `tools/panel/serwer.py` do czasu wylogowania.
Odrzucone: na produkcji API jest w `wsgi.py`, więc lokalny serwer nie jest potrzebny;
uruchamianie procesów z żądania HTTP zamienia błąd uwierzytelniania w zdalne wykonanie kodu;
przy Basic Auth nie istnieje moment „wylogowania", w którym dałoby się taki proces zatrzymać.

### 31. Stary bytecode na serwerze — ZAMKNIĘTE 2026-09-02

`__pycache__` usunięty z serwera, `__pycache__/` jest w `.gitignore` od `09178bc`.
Ostatecznie nie to okazało się przyczyną (#29), ale plik i tak nie miał prawa być w repozytorium.

### 32. Zduplikowany unit `winnicakielnagora.pl.service` — ZAMKNIĘTE 2026-09-03

`systemctl disable` zwrócił „Unit file … does not exist" — plik unitu już nie istnieje.
Stary proces działał w cgroup po unicie usuniętym wcześniej z dysku, więc po jego zabiciu
nie ma czego wskrzeszać przy starcie maszyny.

Warto sprawdzić po najbliższym restarcie serwera, czy port 8004 zajmuje właściwa usługa:
`sudo ss -ltnp | grep 8004` — linia poleceń ma zawierać `--timeout 300`.

### 33. Panel i cennik na serwerze — ZAMKNIĘTE 2026-09-02

`/zdrowie` potwierdza: `panel_wlaczony: true`, cennik czytany z
`/opt/apps/app_winnicakielnagora.pl/dane/wina.json`, czyli spoza katalogu wdrożenia.
Sprawdzone z zewnątrz: pliki panelu za Basic Auth (401), `serwer.py`/`haslo.py`/`README.md`
→ 404, `/data/wina.json` zasiane z wersji startowej w repozytorium.

### 36. Style strony 404 weszły do repozytorium moim commitem

`assets/css/custom.css` dostało 41 reguł `error-page` w commicie `10e0209` (moim) — to była
niezacommitowana praca projektanta, zgarnięta przez `git add -A`. Sama praca jest w porządku,
ale autorstwo w historii jest mylące.

**Wniosek na przyszłość:** przed `git add -A` sprawdzać `git status` i commitować wybiórczo,
gdy ktoś pracuje równolegle. (Ten sam błąd wcześniej ze zrzutami audytu.)
