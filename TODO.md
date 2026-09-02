# TODO — znane braki i rozjazdy

Rejestr rzeczy, które w kodzie już są niespójne, świadomie niedokończone albo czekają na dane
od Właściciela. To nie jest backlog funkcji. Przeczytaj przed większą zmianą; po zamknięciu
pozycji usuń ją i dopisz regułę do `.ai/standards/` lub `.ai/GUARDRAILS.md`.

Ostatnia aktualizacja: **2026-09-02**.

## Do naprawy

### ~~1. Rozjazd ceny netto~~ — ZAMKNIĘTE 2026-09-02

Atrapy produktów usunięte, netto jest wyliczane z `cena_brutto`.

### ~~2. Filtr cenowy ma zaszyty zakres 0–100 zł~~ — ZAMKNIĘTE 2026-09-02

Zakres liczy `zakresCen()` z cen w `data/wina.json`.

### ~~3. Martwe atrybuty `data-price-net` i `data-discount`~~ — ZAMKNIĘTE 2026-09-02

Karty renderuje `Produkty.renderProductCard()`; oba atrybuty zniknęły.

### ~~4. VAT 23% zaszyty w dwóch miejscach~~ — ZAMKNIĘTE 2026-09-02

Stawka pochodzi z `data/wina.json`, etykieta koszyka budowana jest z niej (`#cart-tax-label`).

### ~~5. `wsgi.py` nigdy nie zwraca 404~~ — ZAMKNIĘTE 2026-09-02

Nieznany adres zwraca `404.html` z kodem 404. Przy okazji zawężono zbiór serwowanych plików
(patrz niżej) i dodano obsługę adresów bez `.html`.

**Uwaga na przyszłość:** `wsgi.py` ma teraz listę `KATALOGI_PUBLICZNE`. Nowy katalog, który
ma być widoczny publicznie (np. `filmy/`), trzeba do niej dopisać — inaczej zwróci 404.

## Do decyzji Właściciela

### ~~6. Rozjazd treści: odmiany vs. produkty w sklepie~~ — ZAMKNIĘTE 2026-09-02

Zmyślone produkty usunięte. Sklep buduje się z `data/wina.json`, dziś pustego —
pokazuje „Oferta w przygotowaniu" do czasu wprowadzenia asortymentu (#10).

### 7. Koszyk i formularz są zaślepkami

- Koszyk to `Map` w pamięci — znika po odświeżeniu strony.
- Formularz kontaktowy robi `preventDefault()` + `alert()`, nie wysyła nic; przycisk płatności
  też kończy się `alert()`.
- **Pytanie**: czy i kiedy dokładamy backend (wysyłka maila, trwały koszyk, płatności)? To
  zadanie rozmiaru **L**.
- **Uwaga dla agentów**: `alert()` zawiesza automatyzację przeglądarki — tych przycisków nie
  klikaj przez Chrome MCP.

### 8. `dist/public` — build, którego nie ma

- **Gdzie**: `wsgi.py` → `STATIC_CANDIDATES`
- **Stan**: kod preferuje `dist/public`, ale wdrożenie nie ma kroku budowania, więc na produkcji
  serwowany jest katalog repo. Gałąź `dist/public` jest martwa.
- **Pytanie**: dodajemy build, czy usuwamy tę gałąź z `wsgi.py`?

## Brakujące dane do strony

Bez tych informacji na stronie zostają atrapy. Nie da się ich zgadnąć ani wyprowadzić
z materiałów w `docs/`.

### 9. Dane kontaktowe

Zmyślone dane **zostały usunięte 2026-09-02** — sekcja mówi dziś „Kielnarowa, ok. 10 km od
centrum Rzeszowa" i uczciwie zaznacza, że reszta będzie podana. Zniknęła też mapa Google, bo
wskazywała współrzędne w okolicach Ustrzyk Dolnych; na jej miejscu jest zdjęcie winnicy.

Nadal potrzebne: **dokładny adres, telefon, e-mail**, a jeśli ma być sprzedaż — także NIP
i dane do faktury. Po uzupełnieniu warto przywrócić mapę i dodać `Organization` w JSON-LD.

### ~~10. Asortyment i cennik~~ — ZAMKNIĘTE 2026-09-03

Właściciel wprowadził cennik panelem: 7 win (3 czerwone, 4 białe) i sok winogronowy.
Dane żyją na produkcji w `/opt/apps/app_winnicakielnagora.pl/dane/wina.json`; w repozytorium
`data/wina.json` jest wersją startową (patrz #26 i #34).

Sklep na stronie renderuje się z tych danych — zakres filtra cenowego liczy się sam
(15–222 zł), kategorie też pochodzą z pliku.


### ~~11. Adresy stron odmian bez `.html`~~ — ZAMKNIĘTE 2026-09-02

Na produkcji `/wina/monarch` działa tak samo jak `/wina/monarch.html`. Linki w HTML-u zostają
z rozszerzeniem, bo `python3 -m http.server` używany lokalnie tej sztuczki nie zna — a `canonical`
i tak wskazuje wariant z `.html`, więc nie ma duplikatu dla wyszukiwarek.

### ~~12. Svenson Red~~ — ZAMKNIĘTE 2026-09-02

Właściciel potwierdził, że wino z tej odmiany jest produkowane. Strona odmiany powstała.
Do poprawienia przy okazji: pisany opis winnicy w materiałach jej nie wymienia.

### 13. Wydarzenia i degustacje

Trzy zmyślone terminy z cenami **zostały usunięte 2026-09-02**. Sekcja mówi teraz, że degustacje
odbywają się po wcześniejszym umówieniu, i kieruje do formularza kontaktowego. Usunąłem też
niepotwierdzone obietnice („profesjonalny sommelier", „catering lokalnych produktów", „wesela").

Do decyzji: czy te usługi faktycznie są w ofercie i czy mają wrócić na stronę, oraz czy
chcecie prowadzić kalendarz konkretnych wydarzeń.

## Materiały

### 14. Zgody na wizerunek

Część zdjęć pokazuje rozpoznawalne osoby przy zbiorach i gości winnicy. W nazwach plików
w `attached_assets/photos/` mają one człon **`-osoby-`**. Do czasu potwierdzenia zgód
na stronie używamy wyłącznie kadrów bez tego członu.

### 15. Brakujące ujęcia

W materiałach nie ma zdjęć **butelek z etykietami**, **wnętrza do degustacji** ani ujęcia
budynku innego niż `winnica-budynek-01`. Strona pokazuje dziś w tych miejscach grafiki AI
(`attached_assets/generated_images/`). Potrzebna sesja zdjęciowa albo zgoda na dalsze
korzystanie z grafik zastępczych.

### 16. Filmy — czekamy na linki z YouTube

**Decyzja z 2026-09-02:** filmy trafią na YouTube, Właściciel dostarczy linki później.
Nie kompresujemy ich więc do `filmy/` ani nie hostujemy u siebie.

Do zrobienia po otrzymaniu linków: sekcja z osadzonymi filmami (najlepiej lazy — miniatura
plus odtwarzacz dopiero po kliknięciu, żeby YouTube nie ładował skryptów przy każdym wejściu)
oraz `VideoObject` w JSON-LD, jeśli filmy mają się pojawiać w wynikach wyszukiwania.

Katalog `filmy/` zostaje — przyda się na miniatury albo pliki lokalne, gdyby coś nie miało
trafić na YouTube.

## Higiena repo

### 17. `.claude/skills/` i `.claude/agents/` są w `.gitignore`

Po świeżym klonie nie ma komend `/…` ani subagentów. Odtworzyć powinien je
`t-shirt-size-install.sh`, ale **instalator kopiuje z katalogów `skills/` i `agents/`, których
w repo nie ma** — dziś jedyna kopia frameworka to lokalne `.claude/`. Do rozstrzygnięcia:
commitować `.claude/`, czy dodać katalogi źródłowe.

### ~~18. Przegląd strony w przeglądarce~~ — WYKONANY 2026-09-02

Sprawdzone: strona główna i strona odmiany w motywach `classic`, `modern` i `rustic`, sklep
renderowany z cennika (8 pozycji), zakres filtra policzony z danych (15–222 zł), opcje kategorii
z JSON-a, dodanie do koszyka, etykieta VAT, blok „Wina z tej odmiany", konsola bez błędów.

**Przegląd od razu wykrył błąd**, którego testy nie widziały: `fetch("./data/wina.json")`
działał na stronie głównej, ale na `/wina/*.html` szukał `/wina/data/wina.json` i cicho
wpadał w tekst zastępczy. Naprawione — ścieżki liczą się teraz z adresu `main.js`.

Zostaje do obejrzenia: **układ na telefonie** (nie sprawdzałem szerokości mobilnych).

### 19. Treści stron odmian nie były weryfikowane wobec źródeł

Opisy na ośmiu stronach w `wina/` powstały z rozwinięcia tekstów, które już były na stronie
głównej, plus potwierdzonych faktów o winnicy z materiałów Właściciela. **Nie korzystałem
z linków do Wikipedii i katalogów szkółek** wskazanych w `docs/` — SPEC-001 wymaga
zweryfikowania ich przez WebFetch przed użyciem jako źródło.

Warto je przejrzeć pod kątem zgodności z faktami o odmianach (aromaty, odporność, typowe
zastosowanie) przed publikacją strony.

### 20. Pomoc w opisie — nazwa modelu i koszty

Panel woła OpenAI (`/v1/chat/completions`) przez bibliotekę standardową Pythona, bez pakietu
`openai`. Otwarte sprawy:

- **Domyślny model to `gpt-4o-mini`** — wybrany jako tani i powszechnie dostępny, ale nazw
  modeli nie dało się zweryfikować w tej sesji. Jeśli API odpowie błędem o nieznanym modelu,
  ustaw `OPENAI_MODEL` na aktualną nazwę; kod nie wymaga zmian.
- **Funkcja nie została przetestowana z prawdziwym kluczem** — sprawdzone są tylko ścieżki
  błędów (brak klucza → 400, zbyt długi tekst → 400, brak połączenia → 502, klucz nie trafia
  do logów). Pierwsze użycie z realnym kluczem warto obejrzeć.
- **Treść wychodzi na zewnątrz.** Panel ostrzega przy polu, ale warto o tym pamiętać przy
  wklejaniu czegokolwiek poza notatkami o winie.

### ~~21. Kategorie Dornfeldera i Monarcha~~ — ZAMKNIĘTE 2026-09-03

Poprawione przez Właściciela w panelu. Na produkcji: Dornfelder, Monarch i Swenson Red
mają „Czerwone", pozostałe cztery odmiany „Białe" — czyli **3 czerwone i 4 białe**,
zgodnie z opisem winnicy z materiałów źródłowych.

Do potwierdzenia drobiazg: Właściciel napisał „4 czerwone i 3 białe", co jest odwrotnością
stanu w danych. Jeśli któreś wino ma się jeszcze przenieść — poprawka zajmuje chwilę
w panelu.


### 23. Sklep obiecuje dostawę, której nie ma

Nagłówek sekcji sklepu mówi „Wszystkie produkty dostępne **z dostawą do domu**", a koszyk jest
zaślepką — przycisk płatności kończy się `alert()`. To ten sam gatunek problemu, co usunięte
wcześniej zmyślone wydarzenia: obietnica bez pokrycia.

Do decyzji: usunąć wzmiankę o dostawie do czasu uruchomienia sprzedaży, czy opisać, jak
zamówienie faktycznie działa (np. telefonicznie albo mailem po ustaleniu). Podobnie ogólnikowe
są „Odkryj naszą kolekcję wyjątkowych win" i „Odkryj wyjątkowy smak win produkowanych z pasją"
w hero — do przepisania przy okazji prac nad treścią.

### 24. „Bieszczadzkie stoki" a lokalizacja winnicy

Hasło w hero brzmi teraz **„Tradycyjne wina z bieszczadzkich stoków"** (na polecenie Właściciela,
2026-09-02). Warto to zweryfikować: winnica leży w **Kielnarowej pod Rzeszowem**, a Bieszczady
to pasmo ok. 100 km na południowy wschód. Reszta strony — tytuł, opisy meta, sekcja „O nas",
strony odmian — mówi konsekwentnie o Kielnarowej i okolicach Rzeszowa.

Jeśli to skrót myślowy marketingowy, zostaje. Jeśli nie — naturalniejsze byłoby np.
„Tradycyjne wina z podkarpackich stoków" albo „…ze stoku nad Rzeszowem", i wtedy hasło
zgadzałoby się z resztą treści oraz z lokalizacją, którą podajemy wyszukiwarkom.

### 25. Wnioski z audytu projektanta (2026-09-02)

Pełny raport: `audit/2026-09-02-homepage/AUDIT.md`. Poza rzeczami już zrobionymi (nazwa marki,
`WebSite` JSON-LD, metadane Open Graph) zostają:

- **Krytyczne, mobilne:** nagłówek H1 i ikona wychodzą poza viewport na 390 px — strona wygląda
  na uciętą.
- Nawigacja sekcyjna i CTA to `<button data-scroll>`, a nie `<a href="#sekcja">` — brak
  indeksowalnej siatki linków wewnętrznych i gorsza obsługa klawiaturą.
- „Degustacje" i „Wydarzenia" w menu prowadzą do tej samej sekcji.
- Siedem rozbudowanych kart odmian zajmuje większość strony głównej; na telefonie droga do
  sklepu i kontaktu jest bardzo długa. Odstępy `py-20` nie zmniejszają się na małych ekranach.
- Brakuje nazw dostępności przy przyciskach stylu, koszyka i menu oraz `aria-expanded`.
- Brak linku „Przejdź do treści", widocznego fokusu spójnego z motywami i obsługi
  `prefers-reduced-motion`.
- Nagłówek stron odmian na telefonie: przyciski różnej wysokości, „Nasze odmiany" łamie się
  na dwa wiersze.

`Organization` w JSON-LD celowo pominięte do czasu uzupełnienia adresu, telefonu i logo
(pozycja #9) — tak też rekomenduje audyt.

### ~~26. Zmiany cennika na produkcji vs. git~~ — ROZSTRZYGNIĘTE 2026-09-02

**Wariant A: wdrożenie pomija `data/`.** Żywy cennik mieszka poza katalogiem aplikacji,
a `data/wina.json` w repozytorium jest wersją startową.

Do ustawienia w konfiguracji wdrożeniowej:

```
CENNIK_SCIEZKA=/opt/apps/app_winnicakielnagora.pl/dane/wina.json
```

Plus dwie rzeczy po stronie serwera:

1. Katalog `dane/` **poza** katalogiem synchronizowanym z repozytorium, z prawem zapisu
   dla użytkownika, na którym działa gunicorn.
2. Wdrożenie ma pomijać `data/` — gdyby jednak je nadpisywało, nic złego się nie stanie,
   bo aplikacja i tak czyta ze `CENNIK_SCIEZKA`.

Jak to działa: przy pierwszym żądaniu `zapewnij_plik()` kopiuje wersję z repozytorium na
ścieżkę roboczą; kolejne wdrożenia jej nie ruszają. Bez zmiennej (czyli lokalnie) wszystko
działa po staremu, na pliku z repozytorium. Sprawdza to `tools/test-cennik-sciezka.py`.

**Konsekwencja do zapamiętania:** `data/wina.json` w repozytorium przestaje odzwierciedlać
produkcję. Traktuj go jak wersję startową; gdy zechcesz zgrać ceny z powrotem do gita,
skopiuj plik z serwera ręcznie.


### 27. Panel na produkcji wymaga HTTPS

HTTP Basic Auth przesyła login i hasło (zakodowane w base64, nie zaszyfrowane) przy **każdym**
żądaniu. Po HTTP bez TLS każdy po drodze może je odczytać.

Do potwierdzenia: czy `winnicakielnagora.pl` będzie serwowane przez HTTPS z wymuszonym
przekierowaniem z HTTP. Jeśli nie — nie włączaj `PANEL_UZYTKOWNIK` ani `PANEL_HASLO_HASH`.

Warto też rozważyć ograniczenie `/tools/panel/` po adresie IP na poziomie proxy — wtedy nawet
wyciek hasła nie wystarczy, żeby wejść.

### ~~28. Katalog `.git` publicznie dostępny~~ — ZAMKNIĘTE 2026-09-02

Po naprawie #29 ruch przechodzi przez aplikację i lista dozwolonych plików działa.
Sprawdzone na żywo: `/.git/config`, `/wsgi.py`, `/cennik.py`, `/WDROZENIE.md` → **404**.

Warto mimo to dołożyć `location ~ /\.git { deny all; return 404; }` w nginx — wtedy ochrona
nie zależy od tego, czy aplikacja działa.


### ~~29. Aplikacja nie wykonywała aktualnego kodu~~ — ZAMKNIĘTE 2026-09-02

**Przyczyna: dwie usługi systemd dla tej samej aplikacji.** Port 8004 trzymał gunicorn
z 1 września należący do unitu **`winnicakielnagora.pl.service`** (z `.pl`), a `projects_manager`
zarządza unitem **`winnicakielnagora.service`** (bez `.pl`). Nowy proces nie mógł się podpiąć
pod zajęty port, więc odpowiadał kod sprzed doby.

Naprawione zatrzymaniem starego procesu. Po restarcie: `/zdrowie` zwraca `1764551b7f51`,
ładne adresy działają, `.git` i pliki źródłowe dają 404, `/data/wina.json` przychodzi
z naszej trasy (`no-store`).

**Zostaje do zrobienia — patrz #32**, inaczej problem wróci po restarcie maszyny.


### 30. Uruchamianie lokalnego serwera panelu z przeglądarki — odrzucone

Pomysł: przycisk w panelu startujący `tools/panel/serwer.py` do czasu wylogowania.
**Odrzucone 2026-09-02** z trzech powodów: na produkcji API jest w `wsgi.py`, więc lokalny
serwer nie jest do niczego potrzebny; uruchamianie procesów z żądania HTTP zamienia błąd
w uwierzytelnianiu w zdalne wykonanie kodu; a przy Basic Auth nie istnieje moment
„wylogowania", w którym dałoby się taki proces zatrzymać.

### ~~31. Stary bytecode na serwerze~~ — ZAMKNIĘTE 2026-09-02

`__pycache__` usunięty z serwera, `__pycache__/` jest w `.gitignore` od `09178bc`.
Ostatecznie nie to okazało się przyczyną (patrz #29), ale plik i tak nie miał prawa
być w repozytorium.

### ~~32. Zduplikowany unit `winnicakielnagora.pl.service`~~ — ZAMKNIĘTE 2026-09-03

`systemctl disable` zwrócił „Unit file … does not exist" — plik unitu już nie istnieje.
Stary proces działał w cgroup po unicie usuniętym wcześniej z dysku, więc po jego zabiciu
nie ma czego wskrzeszać przy starcie maszyny.

Potwierdzenie, że został jeden unit:

```bash
systemctl list-unit-files | grep winnica     # tylko winnicakielnagora.service
ls /etc/systemd/system | grep winnica
```

Warto sprawdzić po najbliższym restarcie serwera, czy port 8004 zajmuje właściwa usługa:
`sudo ss -ltnp | grep 8004` — linia poleceń ma zawierać `--timeout 300`.


### ~~33. Panel i cennik na serwerze~~ — ZAMKNIĘTE 2026-09-02

`/zdrowie` potwierdza: `panel_wlaczony: true`, cennik czytany z
`/opt/apps/app_winnicakielnagora.pl/dane/wina.json`, czyli spoza katalogu wdrożenia.

Sprawdzone z zewnątrz:

| adres | wynik |
|---|---|
| `/tools/panel/panel.html`, `.css`, `.js`, `/api/wczytaj` | **401** + `WWW-Authenticate: Basic` |
| `/tools/panel/serwer.py`, `haslo.py`, `README.md` | **404** mimo włączonego panelu |
| `/tools/optimize-photos.py` | **404** |
| `/data/wina.json` | 8 pozycji, zasiane z wersji startowej w repozytorium |

Od tej chwili `data/wina.json` w repozytorium jest **wersją startową** — produkcja żyje
własnym plikiem (`TODO.md` #26).

### 34. Cennik z produkcji nie wraca do repozytorium — niski priorytet

Panel działa i Właściciel zapisał już zmianę wyłącznie na serwerze (2026-09-02:
`seyval-blanc-2022` → `seyval-blanc-2023`). Wersja startowa w `data/wina.json` zaczyna się
rozjeżdżać z produkcją — tak jak przewiduje wariant A z #26, ale warto mieć na to nawyk.

Zgranie produkcji do repozytorium:

```bash
scp ops02:/opt/apps/app_winnicakielnagora.pl/dane/wina.json data/wina.json
```

Właściciel uznał to za mało istotne (2026-09-03). Zostaje jako notatka: jedyną kopią
produkcyjnego cennika jest `wina.json.bak` leżący obok oryginału, więc skasowanie katalogu
`dane/` zabiera i cennik, i kopię. Gdyby kiedyś miało to zaboleć — zadanie w
`production_tasks.json` kopiujące plik raz na dobę rozwiązuje sprawę.

