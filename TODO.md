# TODO — znane braki i rozjazdy

Rejestr rzeczy, które w kodzie już są niespójne, świadomie niedokończone albo czekają na dane
od Właściciela. To nie jest backlog funkcji. Przeczytaj przed większą zmianą.

Podział na trzy pliki:

- **`TODO.md`** (ten plik) — sprawy wciąż otwarte, nad którymi pracujemy albo które czekają
  na materiał od Właściciela.
- **`TODONE.md`** — pozycje domknięte, z datą i opisem rozwiązania. Po zamknięciu pozycji
  przenosisz ją tam (i dopisujesz regułę do `.ai/standards/` lub `.ai/GUARDRAILS.md`).
- **`TODO.maybefuture.md`** — sprawy związane ze sprzedażą online oraz świadomie zawieszone.

Ostatnia aktualizacja: **2026-09-11**.

## Do dodania / uzupelnienia

Skill

Global CLAUDE.md + pamięć realnie załatwiają „pamiętaj za każdym razem" — ładują się do kontekstu na starcie każdej sesji. Istnieje już pusty katalog ~/.claude/skills/frontend-design/. Skill ma sens, jeśli chcesz coś wywoływalnego (/frontend-design) z pełnym szablonem startowym HTML (paleta + przełącznik + reset + siatka). Mogę go zbudować — powiedz tylko, czy ma być sam „motyw light/dark", czy szerszy scaffold nowej strony.

## Do naprawy

### 25. Otwarte bullety z audytu projektanta (2026-09-02)

Pełny raport: `audit/2026-09-02-homepage/AUDIT.md`. Zrobione pozycje audytu są w `TODONE.md`
#25. Zostają:

- ~~**Krytyczne, mobilne:** nagłówek H1 i ikona wychodzą poza viewport na 390 px — strona wygląda
  na uciętą.~~ **Zrobione 2026-09-08:** lockup hero (`.flex` z ikoną + `<h1>`) układa się w kolumnę
  poniżej `sm` (`flex-col sm:flex-row`), `<h1>` zmniejszony z `text-4xl` do `text-3xl` w bazie
  (`md:text-6xl` bez zmian). Sekcja ma `overflow-hidden` (dla obrazu), więc za szeroki tytuł był
  ucinany, nie zawijany.
- Siedem rozbudowanych kart odmian zajmuje większość strony głównej; na telefonie droga do
  sklepu i kontaktu jest bardzo długa. Odstępy `py-20` nie zmniejszają się na małych ekranach.
- Brakuje nazw dostępności przy przyciskach stylu, koszyka i menu oraz `aria-expanded`.
- Brak linku „Przejdź do treści", widocznego fokusu spójnego z motywami i obsługi
  `prefers-reduced-motion` (częściowo: `initNavigation` już honoruje `prefers-reduced-motion`
  przy przewijaniu do sekcji).

`Organization` w JSON-LD — **zrobione 2026-09-07** (`TODONE.md` #9 / #25).

### 27. Panel na produkcji wymaga HTTPS

HTTP Basic Auth przesyła login i hasło (base64, nie szyfrowane) przy **każdym** żądaniu.
Po HTTP bez TLS każdy po drodze może je odczytać.

Do potwierdzenia: czy `winnicakielnagora.pl` będzie serwowane przez HTTPS z wymuszonym
przekierowaniem z HTTP. Jeśli nie — nie włączaj `PANEL_UZYTKOWNIK` ani `PANEL_HASLO_HASH`.

Warto też rozważyć ograniczenie `/tools/panel/` po adresie IP na poziomie proxy — wtedy nawet
wyciek hasła nie wystarczy, żeby wejść.

### 35. Długi cache dla CSS i JS wymaga stemplowania wersji

`Cache-Control` dla CSS i JS zostaje na `no-cache` (ETag → 304, jedna runda bez ciała).
Próba `max-age=3600` skończyła się tym, że przeglądarka pokazywała stary `custom.css`
i strona 404 renderowała się bez stylów — a projektant zmienia CSS na bieżąco.

Żeby bezpiecznie wydłużyć cache, adres musi się zmieniać razem z treścią:
`tools/stempluj-zasoby.py` liczący skrót z każdego pliku CSS/JS i przepisujący odnośniki
w HTML na `...style.css?v=ab12cd34`. HTML jest `no-cache`, więc nowa strona natychmiast
wskazuje nowe adresy. Do tego test pilnujący, że skróty w HTML zgadzają się z plikami.

Obrazy i fonty mają już `max-age=2592000` — ich nazwy są stabilne.

### 39. Kontrola konfliktu przy zapisie panelu nie scala zmian

Od 2026-09-11 `zapisz_bezpiecznie()` (`cennik.py`/`wydarzenia.py`) odrzuca zapis, gdy plik
zmienił się od wczytania — patrz `.ai/standards/backend/edycja-wspolbiezna.md`. To wykrywa
utracony zapis (wypadek z dwoma redaktorami naraz), ale **nie scala** zmian: odrzucony zapis
wymaga, żeby redaktor kliknął „Odrzuć zmiany" i wprowadził swoją zmianę ponownie ręcznie.

Świadomie poza zakresem: miękka blokada „ktoś inny to teraz edytuje" przy otwarciu pozycji
(wymagałaby osobnego pliku blokady z czasem wygaśnięcia i obsługi porzuconej karty) oraz
scalanie pól po stronie serwera (wymagałoby przebudowy zapisu z całego pliku na patch
pojedynczej pozycji). Żadne z nich nie jest pilne — sam wypadek (cicha utrata danych) już
nie może się powtórzyć.

## Do decyzji / weryfikacji Właściciela

### 24. „Bieszczadzkie stoki" a lokalizacja winnicy

Hasło w hero brzmi **„Tradycyjne wina z bieszczadzkich stoków"** (na polecenie Właściciela,
2026-09-02). Warto to zweryfikować: winnica leży w **Kielnarowej pod Rzeszowem**, a Bieszczady
to pasmo ok. 100 km na południowy wschód. Reszta strony — tytuł, opisy meta, sekcja „O nas",
strony odmian — mówi konsekwentnie o Kielnarowej i okolicach Rzeszowa.

Jeśli to skrót myślowy marketingowy, zostaje. Jeśli nie — naturalniejsze byłoby np.
„Tradycyjne wina z podkarpackich stoków" albo „…ze stoku nad Rzeszowem".

Do porównania wariantów słowa „tradycyjne" na żywej stronie służy `?slowo=` (`.ai/specs/quick/004`).

## Brakujące dane / materiały

### 14. Zgody na wizerunek — do zebrania na piśmie

Osiemnaście zdjęć w `attached_assets/photos/` z członem **`-osoby-`** pokazuje rozpoznawalne
osoby. Do czasu potwierdzenia zgód strona używa wyłącznie kadrów bez tego członu.

Właściciel zebrał zgody **ustnie przy robieniu zdjęć** (2026-09-03). Formularz do potwierdzenia
ich na piśmie: `attached_assets/docs/form-zgody-rodo/zgoda-wizerunek-formularz.html` — jedna
strona A4, osiem wierszy na podpisy, z klauzulą informacyjną RODO. Przed pierwszym użyciem
trzeba w nim uzupełnić adres, e-mail i telefon winnicy i warto dać go do przejrzenia prawnikowi.

Ponumerowany przegląd zdjęć: `docs/zgody-wizerunek.jpg` + lista `docs/zgody-wizerunek.txt`
(katalog `docs/` w korzeniu repozytorium jest w `.gitignore`, te dwa pliki zostają lokalnie).

Sam formularz jest w repozytorium i **jest serwowany publicznie** pod
`/attached_assets/docs/form-zgody-rodo/zgoda-wizerunek-formularz.html`. `robots.txt` ma
`Allow: /`, więc jest indeksowany. **Decyzja Właściciela (2026-09-03): zostaje tak — nie
dodajemy `Disallow`.** To pusty szablon bez danych osobowych. Nie wracaj do tego bez jego słowa.

**Czego potrzebuję, żeby użyć tych zdjęć:** wyłącznie numery z przeglądu.
**Nie przysyłaj nazwisk ani podpisanych formularzy** — to dane osobowe, a repozytorium jest
publiczne (`.ai/GUARDRAILS.md` → STOP #2).

### 15. Brakujące ujęcia

W materiałach nie ma zdjęć **butelek z etykietami**, **3 pokoi gościnnych** (sekcja
`#noclegi` startuje bez zdjęć — patrz #37) ani ujęcia budynku innego niż `winnica-budynek-01`.
Strona pokazuje dziś w niektórych miejscach grafiki AI (`attached_assets/generated_images/`).
Potrzebna sesja zdjęciowa albo zgoda na dalsze korzystanie z grafik zastępczych.

### 16. Filmy — czekamy na linki z YouTube

**Decyzja z 2026-09-02:** filmy trafią na YouTube, Właściciel dostarczy linki później.
Nie kompresujemy ich do `filmy/` ani nie hostujemy u siebie.

Do zrobienia po otrzymaniu linków: sekcja z osadzonymi filmami (najlepiej lazy — miniatura
plus odtwarzacz dopiero po kliknięciu) oraz `VideoObject` w JSON-LD, jeśli filmy mają się
pojawiać w wynikach wyszukiwania. Katalog `filmy/` zostaje — przyda się na miniatury.

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
  błędów. Pierwsze użycie z realnym kluczem warto obejrzeć.
- **Treść wychodzi na zewnątrz.** Panel ostrzega przy polu, ale warto o tym pamiętać.

### 37. Noclegi — zdjęcia pokoi, udogodnienia, „cena od"

Integracja z Booking **zrobione 2026-09-09**: sekcja `#noclegi` to karta oferty z natywnym
`<form method="get">` (`#noclegi-form`) kierującym na `https://www.booking.com/hotel/pl/winnica-kielna-gora.pl.html`
z parametrami `checkin` / `checkout` / `group_adults` / `no_rooms=1` / `group_children=0`.
Działa bez JS; `initNoclegi()` w `main.js` podpowiada daty jutro/pojutrze i pilnuje
`wyjazd > przyjazd`. Booking.com **nie daje właścicielowi obiektu osadzalnego widgetu** —
osadzalne widgety są tylko przez Affiliate Partner Centre (obcy skrypt `aff.bstatic.com`),
Właściciel świadomie tego nie chce (2026-09-09, GUARDRAILS #6).

Zostaje:
- **Zdjęcia 3 pokoi** (w zasobach nie ma kadru pokoju — patrz #15). Po materiałach wgrać
  3 do `attached_assets/photos/`, odkomentować rząd w karcie: `grid grid-cols-3 gap-3`
  (**nie** `md:grid-cols-3` — nie ma w prebuilt bundlu), `alt` po polsku, `width`/`height`,
  `loading="lazy"`.
- **Lista udogodnień i „cena od"** — komentowane sloty w karcie `#noclegi`, wypełnia
  Właściciel; nie wymyślać wartości.
- **Ręczne potwierdzenie** — Właściciel klika raz przez formularz i sprawdza, czy Booking
  honoruje `checkin` / `checkout` / `group_adults` (WebFetch nie zweryfikuje — Booking
  blokuje boty).

## Higiena repo

### 17. `.claude/skills/` i `.claude/agents/` są w `.gitignore`

Po świeżym klonie nie ma komend `/…` ani subagentów. Odtworzyć powinien je
`t-shirt-size-install.sh`, ale **instalator kopiuje z katalogów `skills/` i `agents/`, których
w repo nie ma** — dziś jedyna kopia frameworka to lokalne `.claude/`. Do rozstrzygnięcia:
commitować `.claude/`, czy dodać katalogi źródłowe.
