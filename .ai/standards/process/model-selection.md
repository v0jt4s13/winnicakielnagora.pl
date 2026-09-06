# Model Selection by Task Type

Agent musi zaproponować zmianę modelu i czekać na akceptację użytkownika — nigdy nie zmienia modelu bez zgody.

## Domyślny dobór modeli

| Zadanie | Model |
|---------|-------|
| Implementation (kod, logika) | **Sonnet 5** |
| Tests, regular debugging | **Sonnet 5** |
| Refactoring | **Sonnet 5** |
| Architecture, design decisions | **Opus 5** |
| Difficult problems (bezpieczeństwo, algorytmy, wielowątkowe) | **Opus 5** |
| Final code review, decisions requiring deep reasoning | **Opus 5** |

## Jak zaproponować zmianę modelu

Jeśli bieżące zadanie wymaga głębszej analizy lub architektonicznego decyzje, agemt pyta użytkownika **zanim zmieni model**:

```
Zadanie wymaga głębokich rozważań architektonicznych. Proponuję zmianę 
na Opus 5 dla większego reasoning. Zgadzasz się?
```

Użytkownik akceptuje eksplicite (`tak`, `ok`, `yes`) albo odrzuca (`nie`, `zostań`, `sonnet`). Agent nie zmienia modelu bez zgody.

## Wyjątki

- Modele mogą się zmieniać wraz z wydaniami nowych wersji — lista powyżej odzwierciedla stan **wrzesień 2026**
- L-sized specyfikacje zawsze idą na Opus 5 przed implementacją
- Trudne błędy znalezione w trakcie implementacji mogą wymagać switch na Opus 5 — zaproponuj wtedy
