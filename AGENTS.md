# AGENTS.md — winnicakielnagora.pl

Statyczna witryna winnicy (jeden `index.html` + `assets/`), serwowana przez 16-liniowy
Flask. Projekt pracuje w **t-shirt size workflow**, ale framework jest tu świadomie
odchudzony — sekcje, które zakładają warstwy API/DB/UI, zostały wycięte lub przepisane
pod realia trzech plików. Zmiany oznaczone są w tekście.

## ⚠️ Before you start — HARD STOP gate

**This is a blocking rule. No `/` command in this framework may execute while the sections below contain `_(fill in)_` or empty placeholders.**

The user must fill in (themselves, by hand) the following sections of this file:

- [x] **Project Layout** (below) — high-level folder map
- [x] **Tech Stack** (below) — runtime, framework, DB, linter
- [x] **Commands** table (below) — dev, build, test, lint/format
- [x] **Where to Look** table (bottom of this file) — delete rows that don't apply to your stack

And in `.ai/GUARDRAILS.md`:

- [x] At least one project-specific BLOCK rule
- [x] Your architectural decisions section

### Rule for agents

When any `/` command is invoked, your FIRST action is to read this file and check the four sections above.

- If ANY section still contains `_(fill in)_` or an equivalent empty placeholder → **STOP immediately**. Do not proceed with the command. Do not read other files. Do not offer alternative plans.
- Tell the user exactly which sections are empty and that you cannot continue until they fill them in.
- **Do NOT offer to fill them yourself.** Do NOT suggest values. Do NOT proceed even if the user insists — these values must come from the user because they encode project-specific knowledge the agent cannot infer.
- The only exception: reading this file to perform the gate check itself.

Once the sections are filled, the user can re-run the original command and it will proceed normally.

### Why

The framework is stack-agnostic (Node, .NET, Rails, Go, Python, Rust — all work identically). But every command downstream assumes these values are correct. If the agent auto-fills them, it will guess (e.g. "probably PostgreSQL") and the rest of the workflow will propagate those guesses. The gate forces the human to commit to a stack once, explicitly.

Then run `/discover-standards` on your codebase to generate your first standards. Do not copy standards from other projects — they must emerge from your own code.

## Workflow Orchestration

### 1. Specification and plan before coding

- Enter plan mode for non-trivial tasks (3+ steps or architectural decisions); if the task is to make the Specification - you skip the plan mode and start writing the specification directly to the file in the `.ai/specs` (details how to name file etc below),
- if there's an existing and comprehensive specification file you can skip the plan mode and proceed to task creation (the next workflow phase),
- new features should follow the specification file created in the planning phase, this step could be skipped for small improvements (no architecture decisions, less than 3 steps) or bug fixes
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Save context - load only these specification file that is related to the current task at hand or required for it to finish
- **Przed większą zmianą przejrzyj `TODO.md`** — trzyma znane rozjazdy w kodzie (martwe atrybuty,
  zaszyte zakresy, zaślepki). Sporo „błędów", które zobaczysz w kodzie, jest tam już opisanych
  wraz z decyzją, czy w ogóle je naprawiamy.

### 2. Strict Phase Progression (M/L tasks)

**HARD RULE: After completing any phase, propose ONLY the immediate next phase. NEVER skip phases or ask about a later phase.**

The workflow phases for M/L tasks are strictly ordered:

| # | Phase | What you do | What you say to the user after completing |
|---|-------|-------------|-------------------------------------------|
| 1 | **Spec** | Write/verify specification | Run `spec-reviewer` agent on the spec file. If PASS → "Spec verified as self-contained. Next step: task breakdown. Should I proceed?" If NEEDS WORK → follow the Spec Review Loop below. |
| 2 | **Tasks** | TaskCreate all steps + TaskUpdate dependencies | "Tasks created ([N] tasks). Next step: inject relevant standards. I propose injecting: [list]. Confirm?" |
| 3 | **Inject** | `/inject-standards` with confirmed paths | "Standards injected. Ready to start implementation. Should I begin with task #1: [name]?" |
| 4 | **Implement** | Code, one task at a time | Mark each task completed, move to next |
| 5 | **Verify** | `/verify-standards` automatically | Report results, fix if needed |
| 6 | **Build** | Run build for changed packages | Report build status |

**Spec Review Loop (when `spec-reviewer` returns NEEDS WORK):**

1. Present the gaps list to the user
2. Split gaps into two categories:
   - **Auto-fixable** — info exists in your conversation context but wasn't written to spec. Fix these yourself immediately — this is exactly the implicit knowledge that needs to be captured.
   - **Needs user input** — unclear requirements or business decisions. Ask the user.
3. **Verify all URLs** listed in the reviewer's "URLs Requiring Verification" section — use WebFetch on each one. Remove or replace any that don't resolve to the expected content. Ask the user for correct URLs if needed.
4. Update the spec file with all fixes
5. Re-run `spec-reviewer` on the updated spec
6. Repeat until PASS. Do NOT proceed to tasks until the spec passes review.

**Examples of WRONG behavior:**
- ❌ After spec: "Should I start implementing?" (skips tasks + inject)
- ❌ After spec: "Should I inject standards and start coding?" (skips tasks)
- ❌ After tasks: "Let me start coding" (skips inject)

**Examples of CORRECT behavior:**
- ✅ After spec: "Spec is ready. Next step is task breakdown. Should I create tasks?"
- ✅ After tasks: "Tasks ready. Next step is standards injection. I propose injecting: [list]"
- ✅ After inject: "Standards loaded. Starting implementation with task #1: [name]"

### 3. Subagent Strategy

**W tym projekcie subagenci do czytania kodu są stratą czasu i kontekstu.** Cała baza kodu
to ~1500 linii w trzech plikach (`index.html`, `assets/js/main.js`, `assets/css/custom.css`) —
`grep -n` + `sed -n` na konkretnej sekcji jest tańsze i pewniejsze niż `codebase-analyzer`
czy `codebase-pattern-finder`.

Subagenta odpalaj tylko wtedy, gdy praca wychodzi **poza to repo**:

- research zewnętrzny (przepisy o sprzedaży wina online, charakterystyka odmian winorośli),
- równoległe zadanie, które ma wrócić samym wnioskiem, a nie listą plików.

### 4. Self-improvement Loop

- After ANY correction from the user: update specification file or run `/sync-standards` command if it's something more general with the pattern
- Write rules for yourself that prevent the same mistake and suggest updates to `AGENTS.md` files
- Ruthlessly iterate on these lessons until mistake rate drops
- Trwałe wnioski zapisuj tam, gdzie ktoś je znajdzie: reguła o kodzie → `.ai/standards/`,
  granica nie do przekroczenia → `.ai/GUARDRAILS.md`, znany brak → `TODO.md`. Nie ma tu
  osobnego pliku z lekcjami.

### 5. Verification Before Done

- Suggest user to verify the task completeness by proving it works:
  - Diff behavior between main and your changes when relevant
  - Ask yourself: "Would a staff engineer approve this?"
  - Nie ma testów ani logów aplikacji — dowodem jest **podgląd w przeglądarce**
    (patrz „Weryfikacja w przeglądarce"). Napisz, co obejrzałeś i w którym motywie.

### 6. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it
- Follow the project's design principles and rules defined in `GUARDRAILS.md` and `.ai/standards/`

### 7. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Zero context switching required from the user
- Nie ma tu CI, testów ani logów serwera aplikacji — zgłoszenie będzie opisem tego, co widać
  na stronie („koszyk nie przelicza VAT-u", „filtr gubi produkt"). Odtwórz to w przeglądarce,
  znajdź przyczynę w `index.html` / `main.js`, napraw i opisz, jak sprawdzić poprawkę.


## Documentation and Specifications

Architecture Decision Records (ADRs) and feature specifications are maintained in the `.ai/specs/` folder. This serves as the source of truth for design decisions and module specifications. Save context size and load only these specs that are related to and required to finish the task at hand.

### Spec Files (Size L)

- **Naming convention**: `SPEC-{number}-{date}-{title}.md` (e.g., `SPEC-003-2026-01-23-notifications-module.md`)
- **Number**: Sequential identifier (001, 002, 003, etc.)
- **Date**: Creation date in ISO format (YYYY-MM-DD)
- **Title**: Descriptive kebab-case title
- Each spec documents the module's purpose, architecture, API contracts, data models, and implementation details.
- Specs should include a **Changelog** section at the bottom to track evolution over time.

### Quick Specs (Size S)

For small changes (bug fix, field addition, text change) — lightweight plan files in `.ai/specs/quick/`:

- **Naming convention**: `{NNN}-{slug}.md` (e.g., `001-add-dark-mode-toggle.md`)
- **Number**: Sequential identifier within quick specs
- **Content**: Scope, what to change, where, and why — no formal sections required
- Quick specs are disposable — they document intent, not architecture

### When Developing Features

1. **Before coding**: Check if a spec exists for the module you're modifying. Search for `SPEC-*-{module-name}.md` files.
2. **When adding features**: Update the corresponding spec file with:
   - New functionality description
   - API changes
   - Data model updates
   - A changelog entry with date and summary
3. **When creating new modules**: Use the `/create-spec` skill for interactive, guided spec creation. It handles discovery, naming, structure, and file creation following `.ai/specs/AGENTS.md` conventions.

### Spec Changelog Format

Each spec should maintain a changelog at the bottom:

```markdown
## Changelog

### 2026-02-05
- Added email notification channel support
- Updated notification preferences API

### 2026-02-05
- Initial specification
```

### Auto-generating Specs

Even when not explicitly asked to update specs, agents should:

- Generate or update the spec when implementing significant changes
- Keep specs synchronized with the actual implementation
- Document any architectural decisions made during development

This ensures the `.ai/specs/` folder remains a reliable reference for understanding module behavior and history.

## Task Management

> **GATE CHECK**: If you just completed a spec and are about to ask the user "should I start implementation?" — STOP. You are violating phase progression (see §2). The next step is **task creation**, not implementation.

### When to Create Tasks

**ALWAYS after completing or verifying the specification, BEFORE inject standards and implementation.** Tasks are the bridge between spec and code — without them the agent jumps from "what to do" to "doing" without tracking progress.

Order: `spec ready → TaskCreate (all steps) → TaskUpdate (dependencies) → inject standards → implement`

### Task Rules

1. **Atomic steps**: Each task = one file or one logical change (np. „Dodaj sekcję `#degustacje` do index.html", nie „Zrób stronę degustacji")
2. **Dependencies**: Set `blockedBy` — np. obsługa w `main.js` zależy od dodania markupu w `index.html`
3. **Inject standards as task #1**: First task is always injecting standards (blocks the rest)
4. **Track Progress**: Mark `in_progress` before starting, `completed` after finishing
5. **Explain Changes**: High-level summary at each step
6. **Document Results**: Add review section to specification file
7. **Sync to spec**: After creating tasks, write an `## Implementation Checklist` section at the end of the spec file (before Changelog). Update checkboxes as tasks complete. This enables session continuity — if a session breaks mid-implementation, a new session reads the spec and sees what's done vs remaining.
   ```markdown
   ## Implementation Checklist
   - [x] Inject standards
   - [x] Markup sekcji w index.html
   - [ ] Obsługa w main.js (funkcja initX + rejestracja w DOMContentLoaded)    ← in progress
   - [ ] Style w custom.css sprawdzone we wszystkich czterech motywach
   ```

### After Completing Implementation

**When ALL implementation tasks have status `completed` — automatically run `/verify-standards`** without waiting for user command. This is a mandatory step in the `implement → verify` flow. Only after verify (and any fixes) inform the user about readiness to commit.

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Project Layout

```
index.html                # CAŁA witryna — jeden plik, wszystkie sekcje
404.html                  # projektowa strona błędu; <base> podmienia wsgi.py wg przedrostka wdrożenia
wsgi.py                   # Flask: statyki, /data/*.json, API panelu, kadr hero wybierany serwerowo
cennik.py                 # dane cennika — odczyt, walidacja, zapis atomowy (CENNIK_SCIEZKA)
wydarzenia.py             # dane wydarzeń — jw. + filtr widoczności (WYDARZENIA_SCIEZKA)
data/                     # wersje STARTOWE wina.json i wydarzenia.json; żywe pliki leżą poza repo
wina/                     # strony odmian, po jednym pliku HTML na odmianę
assets/
  css/style.css           # prebudowany bundle Tailwind (zminifikowany, 1 linia) — NIE edytować ręcznie
  css/custom.css          # ręcznie pisane style projektu (.btn-primary, .hover-elevate, .cart-panel…)
  js/produkty.js          # biblioteka: wyliczenia cen i render karty; NIC nie uruchamia przy wczytaniu
  js/main.js              # cały front-end: motywy, nawigacja, filtry, koszyk, wydarzenia, formularz
tools/                    # skrypty uruchamiane ręcznie: dev-server, panel, testy, optymalizacja zdjęć
attached_assets/
  generated_images/       # grafiki witryny (hero, butelki, wnętrza) — PNG + jeden JPG
  photos/hero/            # czasowe kadry hero — WebP; mastery PNG poza repo, patrz lokalny README
  docs/                   # formularz zgody na wizerunek — serwowany publicznie
.ai/                      # GUARDRAILS.md, specs/, standards/ — workspace workflow t-shirt size
.claude/agents/           # subagenci — UWAGA: katalog jest w .gitignore, po klonie go nie ma
.claude/skills/           # komendy /inject-standards, /verify-standards… — też w .gitignore
t-shirt-size-install.sh   # instalator frameworka (patrz TODO.md — brakuje mu katalogów źródłowych)
TODO.md                   # znane braki i rozjazdy w kodzie — przeczytaj przed większą zmianą
AGENTS.md                 # ten plik; CLAUDE.md to jednolinijkowy stub `@AGENTS.md`
```

Projekt jest jednomodułowy: **nie ma podziału na warstwy, pakiety ani aplikacje**.
Cała logika strony mieści się w `index.html` + `assets/js/main.js`.

## Tech Stack

- **Frontend**: statyczny HTML5 + vanilla JavaScript (ES6, bez frameworka, bez modułów,
  bez bundlera). Jeden plik `assets/js/main.js` ładowany z `defer`.
- **CSS**: Tailwind jako **gotowy, zbudowany artefakt w repo** (`assets/css/style.css`) —
  brak `package.json`, `tailwind.config` i źródeł, więc bundla nie da się przebudować.
  Style dopisywane ręcznie idą do `assets/css/custom.css`. Motywy = zmienne CSS (HSL)
  podmieniane w JS na `document.documentElement`.
- **Fonty**: Google Fonts (Playfair Display + Lato) z CDN — jedyna zewnętrzna zależność runtime.
- **Serwer**: Python 3.11 + Flask (`wsgi.py`) wyłącznie do serwowania plików statycznych.
  Produkcja: gunicorn `wsgi:app` na `127.0.0.1:8004`, domena `ops02.jdblayer.com`,
  katalog `/opt/apps/app_winnicakielnagora.pl`, wdrożenie przez `projects_manager`.
- **Baza danych**: brak silnika bazodanowego. Dane redagowane panelem żyją w dwóch plikach
  JSON — `data/wina.json` i `data/wydarzenia.json` — obsługiwanych przez `cennik.py`
  i `wydarzenia.py`. Na produkcji ich żywe wersje leżą **poza katalogiem wdrożenia**
  (`CENNIK_SCIEZKA`, `WYDARZENIA_SCIEZKA`), a kopie w repo są wersjami startowymi.
  Koszyk żyje w pamięci (`Map` w `main.js`), wybrany motyw w `localStorage`
  pod kluczem `winery-style`.
- **Motywy**: cztery zestawy (`classic`, `modern`, `rustic`, `dark`), po 29 zmiennych CSS
  każdy, w obiekcie `themeStyles` na górze `main.js`. Muszą pozostać w parytecie.
  `dark` jest jedynym ciemnym i jedynym, który witryna włącza sama — po zmroku,
  przez `initTimeTheme()`.
- **Ceny**: `data-price` na karcie produktu to **brutto**; netto i VAT 23% liczy
  `renderCart` (`subtotal / 1.23`). Nie ma nigdzie osobnego źródła cen.
- **Testy**: brak. **Linter / formatter**: brak. **Krok budowania**: brak.

## Commands

| Action | Command |
|---|---|
| Dev | `python3 tools/dev-server.py --port 5000` w katalogu repo → http://localhost:5000 (zero zależności, obsługuje projektowe `404.html`; Flask/gunicorn nie są zainstalowane lokalnie). Wariant produkcyjny: `python3 -m flask --app wsgi run --port 8004` |
| Build | **brak** — `assets/css/style.css` jest w repo jako gotowy artefakt; nic się nie kompiluje |
| Test | **brak** — jedyna weryfikacja to podgląd strony w przeglądarce; opisz w odpowiedzi, którą sekcję i co sprawdzić |
| Lint / Format | **brak** — trzymaj się formatowania sąsiedniego kodu (2 spacje wcięcia w HTML/JS/CSS) |

## Coding Standards

Detailed standards: `.ai/standards/`
Index: `.ai/standards/index.yml`

**Before any non-trivial change** — przeczytaj właściwy standard. Obszary w tym projekcie:

- Treść i dane zaszyte w HTML → `.ai/standards/content/`
- Front-end: JS, motywy, style → `.ai/standards/frontend/`

Format standardu pokazuje `.ai/standards/HOW-A-STANDARD-LOOKS.md`.

Available skills:

- `/inject-standards` — inject standards into context
- `/discover-standards` — discover new patterns in the code
- `/verify-standards` — verify code vs standards (after implementation)
- `/sync-standards` — synchronize standards with new code (after implementation)
- `/index-standards` — przebuduj `.ai/standards/index.yml` po ręcznej edycji standardów
- `/create-spec` — interaktywne tworzenie specyfikacji w `.ai/specs/`

## Workflow (Feedback Loop)

Classification and flow:

```
S: inject → implement → verify → przegląd w przeglądarce
M: inject(propose) → plan(+user-stories) → tasks → implement → verify → przegląd w przeglądarce → sync-standards
L: discover → inject(propose) → spec(+user-stories) → tasks → implement → verify → przegląd w przeglądarce → sync-standards
```

- `tasks` — after completing/verifying spec, BEFORE implementation: break down tasks with dependencies (TaskCreate + TaskUpdate). Tasks are atomic implementation steps derived from the spec.
- `inject(propose)` — read index.yml, propose specific standards, after confirmation `/inject-standards` explicit
- Fazy `+analogies` i `+pattern-finder` z oryginalnego szablonu **są wycięte** — patrz
  „Nawigacja po kodzie" niżej.
- `build` zastąpiony **przeglądem w przeglądarce** — w tym projekcie nie ma czego zbudować.

Standards are a living document — every implementation either confirms standards or updates them.

### Klasyfikacja rozmiaru w tym projekcie

| Rozmiar | Co to znaczy tutaj | Przykłady |
|---|---|---|
| **S** | zmiana treści lub atrybutu, bez nowego zachowania | poprawka tekstu, podmiana zdjęcia, zmiana ceny produktu, nowy punkt listy |
| **M** | nowa sekcja strony albo zmiana zachowania w `main.js` | sekcja `#degustacje`, nowy filtr w sklepie, zmiana logiki koszyka |
| **L** | funkcja wymagająca czegoś, czego projekt nie ma (backend, baza, build, integracja) | realna wysyłka formularza, płatności, trwały koszyk, przebudowa Tailwinda ze źródeł |

**L prawie zawsze oznacza rozmowę z Właścicielem przed napisaniem kodu** — dokłada projektowi
zależność, której świadomie nie ma (patrz `.ai/GUARDRAILS.md` → Architectural decisions).

### Weryfikacja w przeglądarce (zamiast builda)

Nie ma builda ani lintera — `/verify-standards` nie odpali tu żadnego narzędzia (jego
`allowed-tools` zna tylko biome/eslint/prettier/ruff/dotnet format/gofmt/rustfmt). Zamiast
builda, zanim zgłosisz zmianę jako gotową:

1. `python3 tools/dev-server.py --port 5000` w katalogu repo → http://localhost:5000
2. Obejrzyj sekcję, której dotyczyła zmiana (kotwice w tabeli **Where to Look**)
3. **Przełącz wszystkie cztery motywy** (menu stylu w nagłówku) — każda zmiana kolorów lub CSS
   musi wyglądać poprawnie w `classic`, `modern`, `rustic` i `dark`
4. Przy zmianach w sklepie: sprawdź filtry (kategoria, zakres cen, „tylko promocje") oraz
   koszyk (dodanie, +/−, podsumowanie netto / VAT / razem)
5. Konsola przeglądarki bez błędów
6. W odpowiedzi napisz, co konkretnie sprawdziłeś i czego sprawdzić się nie dało

**Nie klikaj „Przejdź do płatności" ani „Wyślij" w automatyzacji przeglądarki** — oba wołają
`alert()`, który zawiesza sesję Chrome MCP (patrz Gotchas).

### Standards Injection Protocol (M/L tasks)

Standardy dokumentują reguły; sam kod czytaj wprost (jest tani). Zanim zaczniesz:

1. **Read the index** — `.ai/standards/index.yml`
2. **Match to task** — dobierz obszary do treści zadania
3. **Propose to user** konkretne ścieżki, np.:

   > Zadanie dotyczy dodania produktu do sklepu. Proponuję wstrzyknąć:
   > - `content/product-card` — atrybuty `data-*`, brutto/netto/VAT, co czyta JS
   > - `content/html-editing` — jak edytować `index.html`, ikony, wcięcia
   >
   > Potwierdzasz? Chcesz coś dodać lub usunąć z listy?

4. **After confirmation** — `/inject-standards` w trybie jawnym:
   ```
   /inject-standards content/product-card content/html-editing
   ```
5. **DO NOT use** auto-suggest mode (`/inject-standards` bez argumentów) dla M/L — zawsze
   proponuj konkretne standardy

### Nawigacja po kodzie (zamiast Analogy Discovery / Pattern Finder)

Oryginalny szablon przewiduje w tym miejscu dwie fazy z subagentem `codebase-pattern-finder`:
szukanie analogicznego modułu i szukanie przykładu kodu. **W tym projekcie obie są wycięte** —
nie ma modułów ani warstw, a całość mieści się w trzech plikach. Zamiast tego:

| Czego szukasz | Jak to znaleźć |
|---|---|
| sekcja strony | `grep -n 'id="nazwa-sekcji"' index.html`, potem `sed -n 'A,Bp' index.html` |
| zachowanie front-endu | `grep -n '^function' assets/js/main.js` — każde `initX()` to jeden obszar |
| wzór markupu (np. karta produktu) | skopiuj sąsiedni element z tej samej sekcji — to jedyny obowiązujący wzorzec |
| klasa CSS | `grep -n '^\.' assets/css/custom.css`; jeśli nie ma — sprawdź, czy klasa jest w bundlu Tailwinda |
| dokumentacja biblioteki zewnętrznej | Context7 (`resolve-library-id` + `query-docs`) — **nigdy WebSearch** |

Wycięte sekcje („Analogy Discovery", „Code Pattern Finder", „Summary: 3 Tools Instead of
Explore") są w historii gita, gdyby projekt kiedyś urósł.

### User Stories (plan/spec phase — M/L only)

Po klasyfikacji rozmiaru, a przed opisem rozwiązania — **napisz scenariusze użytkownika**.
Szczegółowe wytyczne: `.ai/specs/AGENTS.md` → „User Stories Guidelines".

**Dlaczego mają tu sens:** witryna jest w całości UX-em — nie ma logiki serwerowej, którą
można by opisać osobno. Scenariusz jest więc jedynym miejscem, gdzie widać, co zmiana robi.

**Jak je pisać w tym projekcie:**

1. **2–3 persony** — realne dla winnicy: zwiedzający szukający informacji o winnicy, klient
   kupujący wino w sklepie, osoba rezerwująca wydarzenie/degustację
2. **Krok po kroku przez ekran** — co użytkownik widzi (szkic ASCII) + co się dzieje pod
   spodem (**która sekcja `index.html`, która funkcja `initX()` w `main.js`, jaki stan**)
3. **„Zmiana vs. stan obecny"** przy każdym kroku, który rusza istniejące zachowanie — to
   najtańszy sposób, żeby nie zepsuć działającej strony
4. **Tabela porównawcza**, jeśli funkcja ma warianty albo zastępuje obecne zachowanie
5. **Trzeci scenariusz na przypadki brzegowe** (spec L) — pusty koszyk, brak wyników filtra,
   telefon zamiast desktopu, przełączony motyw

## Gotchas

- **NEVER invent URLs.** If a spec or code needs an external URL — ask the user for the real link or verify it exists via WebFetch. Hallucinated URLs are a real problem — many sites return custom pages (not 404) for non-existent paths, making fake links hard to detect later.
- **Use Context7 for library documentation**, not training-data memory — library APIs drift and your recall can be stale.

### Pułapki tego projektu

- **`assets/css/style.css` to zbudowany Tailwind bez źródeł w repo.** Klasa Tailwinda, której
  nie ma w bundlu, po prostu nie zadziała i nie da się jej „dobudować" — nie ma `package.json`
  ani `tailwind.config`. Nowe style pisz w `assets/css/custom.css` albo użyj klasy, która
  w bundlu już jest.
- **Zmiana ceny produktu to sześć miejsc w `index.html`, nie jedno.** `data-price` (brutto),
  `data-price-net`, widoczny tekst ceny, tekst `netto: … zł`, a przy promocji jeszcze
  przekreślona cena sprzed rabatu i badge `-N%` (plus `data-promo` i `data-discount`). JS czyta **tylko** `data-price`, `data-promo`, `data-category`,
  `data-id`, `data-name`, `data-image` — `data-price-net` i `data-discount` są martwe
  i utrzymywane ręcznie. Szczegóły: `.ai/standards/content/product-card.md`.
- **Filtr cenowy ma zaszyty zakres 0–100 zł** (`input[type="range"]` w sekcji `#sklep`
  oraz `initFilters` w `main.js`). Produkt droższy niż 100 zł zniknie z listy bez żadnego
  komunikatu.
- **VAT 23% jest zaszyty w dwóch miejscach**: `renderCart` w `main.js` (`subtotal / 1.23`)
  i etykieta „VAT (23%)" w panelu koszyka w `index.html`.
- **Cztery motywy po 29 zmiennych CSS.** `setTheme` ustawia je jako style inline na
  `documentElement` i nigdy ich nie czyści — zmienna dodana tylko do jednego motywu zostawi
  po przełączeniu wartość z poprzedniego. Nowa zmienna = wpis we wszystkich czterech obiektach
  `themeStyles`. Szczegóły: `.ai/standards/frontend/theming.md`.
- **Motyw zależny od pory dnia nie może żyć w inicjalizatorze hero.** Podstrony `wina/*.html`
  nie mają `#hero-image`, ale nadal muszą dostać nocny `dark`. Logikę ogólnowitrynową trzymaj
  w osobnym `initTimeTheme()`, a `initHeroImage()` niech odpowiada wyłącznie za obraz.
  Motyw włączany automatycznie ma być **osobną pozycją**, a nie przemalowaniem istniejącej:
  `modern` był przez chwilę ciemny i rozjeżdżał się z własnym opisem w menu.
- **Pomiar `?hero=` nie dowodzi zachowania zwykłego `/`.** Dla obrazu LCP sprawdź produkcyjną
  ścieżkę routingu: preload scanner musi dostać ten sam plik co `src`, bez wcześniejszego
  pobrania fallbacku. Do repozytorium trafiają wyłącznie WebP; mastery PNG leżą **poza repo**,
  w katalogu źródłowym, więc świeży klon nie przekoduje kadrów bez oryginałów od Właściciela.
  Role plików i procedura podmiany: `attached_assets/photos/hero/README.md`.
- **Filtr dat wydarzeń nie może wylądować w `wsgi.py`.** `.ai/GUARDRAILS.md` #3 zabrania
  logiki biznesowej w `wsgi.py` poza panelem redakcyjnym, a `/data/wydarzenia.json` jest trasą
  publiczną. Widoczność liczy `wydarzenia.aktywne()`; handler ma tylko wczytać, zawęzić i oddać.
  Pilnuje tego `tools/test-routing.py`. Wpisy przyszłe i zakończone **nie opuszczają serwera**,
  więc `main.js` nie ma żadnej logiki dat.
- **`alert()` blokuje automatyzację przeglądarki.** „Przejdź do płatności" (`initCart`)
  i wysyłka formularza (`initContactForm`) wołają `alert()` — kliknięcie ich przez Chrome MCP
  zawiesza sesję. Te dwa przyciski testuj ręcznie.
- **Koszyk nie jest trwały** — `Map` w pamięci, znika po odświeżeniu strony. To świadomy stan
  demo; nie „naprawiaj" go bez ustalenia z Właścicielem.
- **Formularz kontaktowy nic nie wysyła** — `preventDefault()` + `alert()`. Nie ma backendu,
  który przyjąłby POST.
- **`wsgi.py` zwraca `index.html` dla każdej nieznanej ścieżki** — status 200, nigdy 404.
  Literówka w linku nigdy się sama nie ujawni; linki sprawdzaj wzrokowo.
- **`wsgi.py` preferuje `dist/public`, jeśli ten katalog istnieje**, a wdrożenie nie ma kroku
  budowania — na produkcji serwowany jest katalog repo. Zanim oprzesz cokolwiek na
  `dist/public`, ustal z Właścicielem, czy build ma powstać.
- **Fonty idą z Google Fonts (CDN)** — bez internetu strona wygląda źle, ale to nie jest błąd CSS.
- **`index.html` to jedyna kopia treści strony**, po polsku, bez i18n i bez kluczy tłumaczeń.
  Zmieniaj dokładnie ten fragment, którego dotyczy zadanie — nie przeformatowuj całości,
  bo diff staje się nieczytelny.
- **Sprawdź `git status` przed pierwszą edycją** — repo bywa zostawiane z niezacommitowaną
  pracą w `index.html` i `attached_assets/`. Nie commituj cudzej pracy razem ze swoją.
- **`.claude/skills/` i `.claude/agents/` są w `.gitignore`** — po świeżym klonie komendy `/…`
  i subagenci nie istnieją (patrz `TODO.md`).
- **Nie dodawaj zależności Pythona bez potrzeby.** Projekt celowo nie ma `requirements.txt`;
  środowisko wymaga tylko Flaska i gunicorna.

## Where to Look

**Nie podawaj w tej tabeli numerów linii** — `index.html` zmienia się przy każdej edycji
treści i numery natychmiast kłamią. Zawsze kotwica: `id`, nazwa klasy, nazwa funkcji.

| What | Where |
|------|-------|
| Serwowanie plików | `wsgi.py` — catch-all `serve()` z białą listą `PLIKI_PUBLICZNE` / `KATALOGI_PUBLICZNE`; nieznany adres to **404**, nie strona główna |
| Endpointy | `wsgi.py` — `/zdrowie`, `/data/wina.json`, `/data/wydarzenia.json` (tylko wpisy aktywne dziś), `/tools/panel/api/<akcja>` za hasłem |
| Sekcje strony | `grep -n '<section id=' index.html` — dziś: `o-nas`, `nasze-wina`, `sklep`, `wydarzenia`, `kontakt` |
| Dane produktów (zamiast bazy) | `data/wina.json` — jedyne źródło asortymentu i cen; `index.html` NIE zawiera kart, renderuje je `renderSklep()` w `main.js`. Reguły: `.ai/standards/content/wina-json.md` |
| Wydarzenia | `data/wydarzenia.json` + `wydarzenia.py` (walidacja, `aktywne()`); render `initWydarzenia()` w `main.js`, kontener `#lista-wydarzen` w sekcji `#wydarzenia` |
| Panel redakcyjny | `tools/panel/` — lokalnie `serwer.py` na `127.0.0.1` bez hasła, na produkcji `wsgi.py` za Basic Auth (`PANEL_UZYTKOWNIK`, `PANEL_HASLO_HASH`) |
| Testy | `tools/test-*.py` — routing, wydarzenia, ścieżka cennika, uwierzytelnianie panelu, serwowanie na prawdziwym Flasku |
| Ikony | `<symbol id="icon-…">` w ukrytym `<svg>` na początku `<body>`, użycie `<use href="#icon-…">` — `grep -n '<symbol' index.html` |
| Koszyk | `assets/js/main.js` — stan w `const cart = new Map()`, render w `renderCart`, zdarzenia w `initCart` (`grep -n 'function initCart' assets/js/main.js`) |
| Motywy | `assets/js/main.js` — obiekt `themeStyles` na górze pliku + `setTheme` / `initStyleSwitcher` |
| Filtry sklepu | `assets/js/main.js` — `function initFilters` (kategoria, zakres cen 0–100, „tylko promocje") |
| Style własne | `assets/css/custom.css` — `grep -n '^\.' assets/css/custom.css`; bundle `assets/css/style.css` tylko do odczytu |
| Grafiki | `attached_assets/generated_images/`; kadry czasowego hero i procedura ich podmiany: `attached_assets/photos/hero/README.md` |
| Znane braki i rozjazdy | `TODO.md` |
