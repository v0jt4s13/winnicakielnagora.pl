"""Walidacja i wysylka wiadomosci z publicznego formularza kontaktowego."""

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import smtplib
import ssl
import tempfile
import time
from email.message import EmailMessage
from pathlib import Path


IKONY = ("wine", "sprout", "square", "users", "map-pin", "clock", "mail")
CZAS_WAZNOSCI_WYZWANIA = 300
MAX_CIAZAR_ZADANIA = 16 * 1024

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PROJEKT = Path(__file__).resolve().parent

# Dane logowania SMTP wpisywane przez Wlasciciela z panelu (zamiast/obok zmiennych
# CONTACT_SMTP_USER/CONTACT_SMTP_PASSWORD) — patrz zapisz_smtp_dane(). Na produkcji
# wskaz je POZA katalog wdrozenia (CONTACT_SMTP_SCIEZKA), ten sam uklad co CENNIK_SCIEZKA.
# Lokalnie ladują do data/ — katalog jest w .gitignore, wiec plik z sekretem nigdy
# nie trafi przypadkiem do repo.
SMTP_DANE = Path(os.environ.get("CONTACT_SMTP_SCIEZKA") or
                  (PROJEKT / "data" / "smtp-dane.json")).expanduser()
# Tylko wlasciciel procesu — to sekret, nie dane redakcyjne jak wina.json (tam 0o640).
PRAWA_PLIKU_SEKRETU = 0o600


class NiepoprawneDane(ValueError):
    """Dane formularza nie spelniaja kontraktu."""


class NiepoprawneWyzwanie(NiepoprawneDane):
    """Token lub wybor ikony nie przechodzi walidacji."""


class SpamRequest(ValueError):
    """Formularz zostal wypelniony przez pole honeypot."""


class BrakKonfiguracji(RuntimeError):
    """Brakuje konfiguracji wyzwania lub SMTP."""


class BladWysylki(RuntimeError):
    """SMTP nie przyjal wiadomosci."""


def _sekret_wyzwania() -> bytes:
    sekret = os.environ.get("CONTACT_CAPTCHA_SECRET", "").strip().encode("utf-8")
    if len(sekret) < 32:
        raise BrakKonfiguracji("CONTACT_CAPTCHA_SECRET musi miec co najmniej 32 znaki")
    return sekret


def _zakoduj(payload: dict) -> str:
    dane = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    zakodowane = base64.urlsafe_b64encode(dane).decode("ascii").rstrip("=")
    podpis = hmac.new(_sekret_wyzwania(), zakodowane.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{zakodowane}.{podpis}"


def _odkoduj(token: str) -> dict:
    if not isinstance(token, str) or token.count(".") != 1:
        raise NiepoprawneWyzwanie("Niepoprawne wyzwanie")
    zakodowane, podpis = token.split(".", 1)
    oczekiwany = hmac.new(_sekret_wyzwania(), zakodowane.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(podpis, oczekiwany):
        raise NiepoprawneWyzwanie("Niepoprawne wyzwanie")
    try:
        padding = "=" * (-len(zakodowane) % 4)
        payload = json.loads(base64.urlsafe_b64decode((zakodowane + padding).encode("ascii")))
    except (ValueError, UnicodeError, json.JSONDecodeError) as blad:
        raise NiepoprawneWyzwanie("Niepoprawne wyzwanie") from blad
    if not isinstance(payload, dict):
        raise NiepoprawneWyzwanie("Niepoprawne wyzwanie")
    return payload


def nowe_wyzwanie() -> dict:
    """Tworzy krotkotrwale wyzwanie wizualne dla przegladarki."""
    opcje = secrets.SystemRandom().sample(IKONY, 6)
    payload = {
        "target": secrets.choice(opcje),
        "options": opcje,
        "expires": int(time.time()) + CZAS_WAZNOSCI_WYZWANIA,
        "nonce": secrets.token_urlsafe(16),
    }
    return {
        "token": _zakoduj(payload),
        "target": payload["target"],
        "options": payload["options"],
        "expires_in": CZAS_WAZNOSCI_WYZWANIA,
    }


def sprawdz_wyzwanie(token: str, wybrana_ikona: str) -> None:
    payload = _odkoduj(token)
    teraz = int(time.time())
    if payload.get("expires", 0) < teraz:
        raise NiepoprawneWyzwanie("Wyzwanie wygaslo")
    opcje = payload.get("options")
    target = payload.get("target")
    if not isinstance(opcje, list) or not all(isinstance(ikona, str) for ikona in opcje):
        raise NiepoprawneWyzwanie("Niepoprawne wyzwanie")
    if set(opcje) - set(IKONY) or target not in opcje or wybrana_ikona != target:
        raise NiepoprawneWyzwanie("Wybierz prawidlowa ikone")


def _tekst(dane: dict, nazwa: str, limit: int, wymagane: bool = True) -> str:
    wartosc = dane.get(nazwa, "")
    if not isinstance(wartosc, str):
        raise NiepoprawneDane(f"Pole {nazwa} ma niepoprawny format")
    wartosc = wartosc.strip()
    if wymagane and not wartosc:
        raise NiepoprawneDane(f"Pole {nazwa} jest wymagane")
    if len(wartosc) > limit:
        raise NiepoprawneDane(f"Pole {nazwa} jest za dlugie")
    return wartosc


def waliduj(dane: dict) -> dict:
    if not isinstance(dane, dict):
        raise NiepoprawneDane("Nieczytelne zadanie")
    if dane.get("website", ""):
        raise SpamRequest("Odrzucono zgloszenie")

    imie = _tekst(dane, "name", 120)
    email = _tekst(dane, "email", 254)
    telefon = _tekst(dane, "phone", 40, wymagane=False)
    wiadomosc = _tekst(dane, "message", 5000)
    if not _EMAIL_RE.fullmatch(email) or "\r" in email or "\n" in email:
        raise NiepoprawneDane("Podaj prawidlowy adres e-mail")
    if "\r" in imie or "\n" in imie or "\r" in telefon or "\n" in telefon:
        raise NiepoprawneDane("Dane formularza zawieraja niepoprawne znaki")

    return {
        "name": imie,
        "email": email,
        "phone": telefon,
        "message": wiadomosc.replace("\r\n", "\n").replace("\r", "\n"),
    }


def wczytaj_smtp_dane() -> dict | None:
    """Dane logowania SMTP zapisane z panelu, albo None gdy pliku nie ma / jest uszkodzony.

    Uszkodzony plik traktujemy jak brak danych (spadamy na zmienne srodowiskowe),
    zamiast wywalac cala wysylke z powodu niezwiazanej awarii dysku.
    """
    if not SMTP_DANE.is_file():
        return None
    try:
        dane = json.loads(SMTP_DANE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(dane, dict):
        return None
    user, password = dane.get("user"), dane.get("password")
    if not isinstance(user, str) or not isinstance(password, str) or not user or not password:
        return None
    return {"user": user, "password": password}


def zapisz_smtp_dane(user: str, password: str) -> None:
    """Zapisuje dane logowania SMTP z panelu — kazdy zapis nadpisuje poprzedni w calosci.

    Haslo aplikacji Gmaila przegladarka pokazuje w czterech grupach ze spacjami
    ("abcd efgh ijkl mnop") — SMTP go nie przyjmie w tej postaci, wiec usuwamy
    biale znaki, zeby wklejenie 1:1 ze strony Google zadzialalo bez tlumaczenia.
    """
    user = (user or "").strip()
    password = re.sub(r"\s+", "", password or "")
    if not user or not _EMAIL_RE.fullmatch(user):
        raise NiepoprawneDane("Podaj prawidlowy adres e-mail konta SMTP")
    if not password:
        raise NiepoprawneDane("Haslo jest wymagane")

    SMTP_DANE.parent.mkdir(parents=True, exist_ok=True)
    tresc = json.dumps({"user": user, "password": password}, ensure_ascii=False) + "\n"
    uchwyt, tymczasowy = tempfile.mkstemp(dir=str(SMTP_DANE.parent), suffix=".tmp")
    try:
        with os.fdopen(uchwyt, "w", encoding="utf-8") as plik:
            plik.write(tresc)
        os.chmod(tymczasowy, PRAWA_PLIKU_SEKRETU)
        os.replace(tymczasowy, SMTP_DANE)
    except BaseException:
        Path(tymczasowy).unlink(missing_ok=True)
        raise


def smtp_skonfigurowane() -> bool:
    """Do statusu w panelu — nie zdradza samych wartosci, tylko czy wysylka zadziala."""
    try:
        _smtp_config()
        return True
    except BrakKonfiguracji:
        return False


def _smtp_config() -> dict:
    host = os.environ.get("CONTACT_SMTP_HOST", "").strip()
    recipient = os.environ.get("CONTACT_TO", "").strip()
    sender = os.environ.get("CONTACT_FROM", "").strip()
    if not host or not recipient or not sender:
        raise BrakKonfiguracji("Brakuje konfiguracji SMTP formularza kontaktowego")
    try:
        port = int(os.environ.get("CONTACT_SMTP_PORT", "587"))
    except ValueError as blad:
        raise BrakKonfiguracji("CONTACT_SMTP_PORT musi byc liczba") from blad

    # Dane z panelu (SMTP_DANE) maja pierwszenstwo przed zmiennymi srodowiskowymi —
    # to one sa teraz zrodlem prawdy, gdy istnieja (decyzja Wlasciciela 2026-09-11).
    z_panelu = wczytaj_smtp_dane()
    if z_panelu:
        user, password = z_panelu["user"], z_panelu["password"]
    else:
        user = os.environ.get("CONTACT_SMTP_USER", "").strip()
        password = os.environ.get("CONTACT_SMTP_PASSWORD", "")
        if bool(user) != bool(password):
            raise BrakKonfiguracji("CONTACT_SMTP_USER i CONTACT_SMTP_PASSWORD musza wystapic razem")

    return {
        "host": host,
        "port": port,
        "recipient": recipient,
        "sender": sender,
        "user": user,
        "password": password,
        "ssl": os.environ.get("CONTACT_SMTP_SSL", "0").strip().lower() in {"1", "true", "yes"},
    }


def wyslij(dane: dict) -> None:
    """Wysyla wiadomosc bez zapisywania jej na dysku ani w bazie."""
    config = _smtp_config()
    wiadomosc = EmailMessage()
    wiadomosc["Subject"] = "Wiadomosc z formularza kontaktowego Winnicy Kielna Gora"
    wiadomosc["From"] = config["sender"]
    wiadomosc["To"] = config["recipient"]
    wiadomosc["Reply-To"] = dane["email"]
    wiadomosc.set_content(
        "Imie i nazwisko: {name}\n"
        "E-mail: {email}\n"
        "Telefon: {phone}\n\n"
        "Wiadomosc:\n{message}\n".format(
            name=dane["name"],
            email=dane["email"],
            phone=dane["phone"] or "(nie podano)",
            message=dane["message"],
        )
    )

    try:
        if config["ssl"]:
            with smtplib.SMTP_SSL(
                config["host"], config["port"], timeout=10,
                context=ssl.create_default_context(),
            ) as smtp:
                if config["user"]:
                    smtp.login(config["user"], config["password"])
                smtp.send_message(wiadomosc)
        else:
            with smtplib.SMTP(config["host"], config["port"], timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                if config["user"]:
                    smtp.login(config["user"], config["password"])
                smtp.send_message(wiadomosc)
    except (OSError, smtplib.SMTPException) as blad:
        raise BladWysylki("Nie udalo sie wyslac wiadomosci") from blad
