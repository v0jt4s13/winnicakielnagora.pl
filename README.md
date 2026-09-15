# winnicakielnagora.pl - szybki start

```bash
git clone git@github.com:v0jt4s13/winnicakielnagora.pl.git
````

```bash
# Dev server (bez SMTP, wystarcza do przeglądania strony)
python3 tools/dev-server.py --port 5000
# → http://localhost:5000

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

# nadawanie uzytkownika i hasla dostepu do panelu
python3 tools/panel/haslo.py
```

## Problem: `git push` → "No anonymous write access" / "Authentication failed"

Ten błąd oznacza dwie osobne rzeczy naraz, obie trzeba naprawić:

1. **Konto na GitHubie nie ma uprawnień do repo.** Właściciel repo (`v0jt4s13`) musi dodać
   Twoje konto jako współpracownika: Settings repo → Collaborators and teams → Add people.
   Bez tego push się nie uda nawet przy poprawnym uwierzytelnieniu.
2. **Remote wskazuje na HTTPS zamiast SSH** - mimo klonowania przez `git@github.com:...`,
   `git push` w błędzie próbuje `https://github.com/...`. Sprawdź i popraw:

```bash
# Sprawdź aktualny adres remote
git remote -v

# Jeśli pokazuje https:// zamiast git@github.com:, zmień na SSH
git remote set-url origin git@github.com:v0jt4s13/winnicakielnagora.pl.git

# Sprawdź, czy masz klucz SSH dodany do konta GitHub
ssh -T git@github.com
```

Jeśli `ssh -T git@github.com` zwraca błąd (brak klucza / Permission denied):

```bash
# Wygeneruj nowy klucz SSH (jeśli jeszcze nie masz)
ssh-keygen -t ed25519 -C "twoj-email@example.com"

# Wyświetl klucz publiczny i dodaj go w GitHub → Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519.pub
```

Jeśli mimo wszystko chcesz zostać przy HTTPS zamiast SSH - GitHub nie akceptuje już haseł
konta, trzeba użyć Personal Access Token jako hasła przy pierwszym `git push`:

```bash
git remote set-url origin https://github.com/v0jt4s13/winnicakielnagora.pl.git
# przy pierwszym push: login = nazwa użytkownika GitHub, hasło = Personal Access Token
# (GitHub → Settings → Developer settings → Personal access tokens)
```

## Praca grupowa (git)

Ustaw raz na maszynę - przy rozjechanych gałęziach `git pull` ma dociągać zmiany
przez rebase (czysta historia, bez commitów „Merge branch..."):

```bash
git config --global pull.rebase true
```

Codzienny cykl pracy:

```bash
# Przed rozpoczęciem pracy - dociągnij najnowsze zmiany
git pull

# Sprawdź co się zmieniło i co masz do commitu
git status
git diff

# Dodaj i zacommituj swoje zmiany
git add <plik>
git commit -m "opis zmiany"

# Wypchnij na GitHub
git push
```

Jeśli `git push` odrzuci z powodu nowych commitów na zdalnym:

```bash
git pull --rebase origin master
git push
```

Jeśli rebase napotka konflikt (dwie osoby zmieniły to samo miejsce w pliku):

```bash
# Git zatrzyma się i pokaże plik z konfliktem - otwórz go, usuń znaczniki
# <<<<<<< / ======= / >>>>>>> i zostaw właściwą wersję, potem:
git add <plik>
git rebase --continue

# Żeby się wycofać z rebase'a i wrócić do stanu sprzed pull:
git rebase --abort
```

Praca nad większą zmianą - osobna gałąź zamiast commitowania prosto na `master`:

```bash
git checkout -b nazwa-galezi
# ... zmiany, commity ...
git push -u origin nazwa-galezi
# potem Pull Request na GitHubie do master
```

Odłożenie niedokończonych zmian, żeby zrobić `git pull` na czystym drzewie:

```bash
git stash
git pull
git stash pop
```
 

# Kompletny proces dodawania dostępu SSH oraz uprawnień administratora (sudo) dla nowego użytkownika `testuser`.

## KROK 1: Lokalnie na komputerze (Wykonuje: Użytkownik testuser)
### Generowanie pary kluczy SSH na własnym komputerze (jeśli klucze nie zostały jeszcze utworzone):
`ssh-keygen -t ed25519 -C "testuser@serwer"`

### Weryfikacja: 
`ls -la ~/.ssh/id_ed25519.pub` - Plik powinien istnieć.
Zawartość pliku należy przekazać administratorowi serwera. Nigdy nie udostępniaj klucza prywatnego (id_ed25519).

## KROK 2: Na serwerze (Wykonuje: Istniejący Admin)
### Utworzenie konta użytkownika testuser i ustawienie hasła:
```
sudo useradd -m -s /bin/bash testuser
sudo passwd testuser
```

### Werryfikacja: 
`id testuser`

### Przyznanie uprawnień sudo:
`sudo usermod -aG sudo testuser`
 (Uwaga: Na systemach z rodziny RedHat/Rocky Linux zamiast grupy sudo używa się grupy wheel: sudo usermod -aG wheel testuser)

### Weryfikacja: 
`groups testuser` - na liście grup użytkownika musi widnieć sudo (lub wheel).

### Konfiguracja klucza SSH dla użytkownika testuser:
```
sudo mkdir -p /home/testuser/.ssh
sudo chmod 700 /home/testuser/.ssh
echo "TUTAJ_ZAWARTOSC_KLUCZA" | sudo tee /home/testuser/.ssh/authorized_keys
sudo chmod 600 /home/testuser/.ssh/authorized_keys
sudo chown -R testuser:testuser /home/testuser/.ssh
```

### Weryfikacja: 
`sudo ls -la /home/testuser/.ssh` - upewnij się, że właścicielem katalogu oraz pliku authorized_keys jest testuser:testuser, a uprawnienia to odpowiednio drwx------ (700) i -rw------- (600).

## KROK 3: Test połączenia i uprawnień (Wykonuje: Użytkownik testuser)
### Logowanie na serwer przez SSH:
`ssh testuser@IP_SERWERA`

### Weryfikacja: 
Powinieneś zalogować się do powłoki serwera bez pytania o hasło (jeśli klucz SSH został poprawnie ustawiony).

### Test uprawnień sudo:
`sudo whoami`
