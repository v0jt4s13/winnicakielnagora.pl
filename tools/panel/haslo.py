#!/usr/bin/env python3
"""Generuje hash hasla do panelu redakcyjnego na produkcji.

Uruchomienie:  python3 tools/panel/haslo.py

Haslo nie jest nigdzie zapisywane — skrypt wypisuje tylko hash, ktory wklejasz
do konfiguracji wdrozeniowej jako PANEL_HASLO_HASH. Do repozytorium NIE trafia
ani haslo, ani hash.
"""
import getpass
import secrets
import sys
from hashlib import pbkdf2_hmac

ITERACJE = 240_000  # musi sie zgadzac z PANEL_ITERACJE w wsgi.py
MIN_DLUGOSC = 12


def main() -> int:
    print("Hash hasla do panelu redakcyjnego.\n")
    uzytkownik = input("Nazwa uzytkownika: ").strip()
    if not uzytkownik:
        print("Nazwa uzytkownika nie moze byc pusta.")
        return 1

    haslo = getpass.getpass("Haslo (min. 12 znakow): ")
    if len(haslo) < MIN_DLUGOSC:
        print(f"Za krotkie — minimum {MIN_DLUGOSC} znakow.")
        return 1
    if haslo != getpass.getpass("Powtorz haslo: "):
        print("Hasla sie roznia.")
        return 1

    sol = secrets.token_bytes(16)
    hash_ = pbkdf2_hmac("sha256", haslo.encode("utf-8"), sol, ITERACJE)

    print("\nDopisz do production_projects/winnicakielnagora.env, w jednej linii")
    print("EXTRA_SYSTEMD_ENV (nie do repozytorium projektu):\n")
    print(f"PANEL_UZYTKOWNIK={uzytkownik}")
    print(f"PANEL_HASLO_HASH={sol.hex()}:{hash_.hex()}")
    print("\nPo restarcie aplikacji panel bedzie pod /tools/panel/panel.html")
    print("Bez tych dwoch zmiennych panel na produkcji nie istnieje (404).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
