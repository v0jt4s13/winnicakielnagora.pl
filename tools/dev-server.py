#!/usr/bin/env python3
"""Lokalny serwer witryny z obsługą projektowej strony 404."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

import kontakt


class ObslugaWitryny(SimpleHTTPRequestHandler):
    def _odpowiedz_json(self, dane: dict, status: int = HTTPStatus.OK) -> None:
        tresc = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(tresc)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(tresc)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/contact/challenge":
            try:
                self._odpowiedz_json(kontakt.nowe_wyzwanie())
            except kontakt.BrakKonfiguracji:
                self._odpowiedz_json(
                    {"ok": False, "komunikat": "Formularz jest chwilowo niedostepny."},
                    HTTPStatus.SERVICE_UNAVAILABLE,
                )
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/contact":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            rozmiar = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._odpowiedz_json({"ok": False, "komunikat": "Nieczytelne zgloszenie."}, 400)
            return
        if rozmiar > kontakt.MAX_CIAZAR_ZADANIA:
            self._odpowiedz_json({"ok": False, "komunikat": "Zgloszenie jest za duze."}, 413)
            return
        try:
            dane = json.loads(self.rfile.read(rozmiar))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._odpowiedz_json({"ok": False, "komunikat": "Nieczytelne zgloszenie."}, 400)
            return
        try:
            kontakt.sprawdz_wyzwanie(dane.get("challenge_token"), dane.get("selected_icon"))
            dane = kontakt.waliduj(dane)
        except kontakt.SpamRequest:
            self._odpowiedz_json({"ok": False, "komunikat": "Nie udalo sie wyslac wiadomosci."}, 400)
            return
        except kontakt.NiepoprawneWyzwanie as blad:
            self._odpowiedz_json({"ok": False, "kod": "challenge", "komunikat": str(blad)}, 400)
            return
        except kontakt.NiepoprawneDane as blad:
            self._odpowiedz_json({"ok": False, "komunikat": str(blad)}, 400)
            return
        try:
            kontakt.wyslij(dane)
        except kontakt.BrakKonfiguracji:
            self._odpowiedz_json(
                {"ok": False, "komunikat": "Formularz jest chwilowo niedostepny."},
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        except kontakt.BladWysylki:
            self._odpowiedz_json(
                {"ok": False, "komunikat": "Nie udalo sie wyslac wiadomosci. Sprobuj ponownie."},
                HTTPStatus.BAD_GATEWAY,
            )
            return
        self._odpowiedz_json({"ok": True})

    def send_error(self, code, message=None, explain=None):
        if code != HTTPStatus.NOT_FOUND:
            return super().send_error(code, message, explain)

        plik_404 = PROJEKT / "404.html"
        if not plik_404.is_file():
            return super().send_error(code, message, explain)

        tresc = plik_404.read_text(encoding="utf-8").replace(
            '<base href="./">', '<base href="/">', 1
        ).encode("utf-8")
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(tresc)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(tresc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "5000")))
    # Domyslnie loopback; --host 0.0.0.0 (albo HOST w srodowisku) wystawia w LAN.
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    args = parser.parse_args()

    # Lokalny serwer moze obslugiwac wyzwanie bez wpisywania sekretu do konfiguracji.
    # Produkcyjny Flask wymaga jawnego CONTACT_CAPTCHA_SECRET.
    os.environ.setdefault("CONTACT_CAPTCHA_SECRET", secrets.token_urlsafe(32))

    handler = partial(ObslugaWitryny, directory=str(PROJEKT))
    with ThreadingHTTPServer((args.host, args.port), handler) as serwer:
        print(f"Winnica: http://{args.host}:{args.port}")
        try:
            serwer.serve_forever()
        except KeyboardInterrupt:
            print("\nSerwer zatrzymany.")


if __name__ == "__main__":
    main()
