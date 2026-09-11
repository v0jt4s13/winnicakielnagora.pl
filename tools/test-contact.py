#!/usr/bin/env python3
"""Testy bez sieci dla walidacji formularza i wyzwania ikon."""

import importlib
import os
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

PROJEKT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJEKT))

import kontakt


SEKRET_TESTOWY = "x" * 32


class FalszywySMTP:
    ostatnia_wiadomosc = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def ehlo(self):
        pass

    def starttls(self, **kwargs):
        pass

    def login(self, *_):
        pass

    def send_message(self, wiadomosc):
        self.__class__.ostatnia_wiadomosc = wiadomosc


class KontaktTest(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "CONTACT_CAPTCHA_SECRET": SEKRET_TESTOWY,
            "CONTACT_SMTP_HOST": "smtp.invalid",
            "CONTACT_SMTP_PORT": "587",
            "CONTACT_SMTP_USER": "",
            "CONTACT_SMTP_PASSWORD": "",
            "CONTACT_SMTP_SSL": "0",
            "CONTACT_FROM": "site@example.invalid",
            "CONTACT_TO": "owner@example.invalid",
        }, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_wyzwanie_akceptuje_prawidlowa_ikone_i_odrzuca_inna(self):
        wyzwanie = kontakt.nowe_wyzwanie()
        kontakt.sprawdz_wyzwanie(wyzwanie["token"], wyzwanie["target"])
        with self.assertRaises(kontakt.NiepoprawneDane):
            kontakt.sprawdz_wyzwanie(wyzwanie["token"], "nieistniejaca")

    def test_wyzwanie_odrzuca_zmieniony_token(self):
        wyzwanie = kontakt.nowe_wyzwanie()
        token = wyzwanie["token"][:-1] + ("0" if wyzwanie["token"][-1] != "0" else "1")
        with self.assertRaises(kontakt.NiepoprawneDane):
            kontakt.sprawdz_wyzwanie(token, wyzwanie["target"])

    def test_wyzwanie_wygasa(self):
        with patch.object(kontakt.time, "time", return_value=1000):
            wyzwanie = kontakt.nowe_wyzwanie()
        with patch.object(kontakt.time, "time", return_value=1000 + kontakt.CZAS_WAZNOSCI_WYZWANIA + 1):
            with self.assertRaises(kontakt.NiepoprawneDane):
                kontakt.sprawdz_wyzwanie(wyzwanie["token"], wyzwanie["target"])

    def test_walidacja_normalizuje_dane_i_odrzuca_honeypot(self):
        dane = kontakt.waliduj({
            "name": "  Test  ",
            "email": "visitor@example.invalid",
            "phone": "",
            "message": "Pierwsza linia\r\nDruga linia",
        })
        self.assertEqual(dane["name"], "Test")
        self.assertEqual(dane["message"], "Pierwsza linia\nDruga linia")
        with self.assertRaises(kontakt.SpamRequest):
            kontakt.waliduj({"website": "wypelnione"})

    def test_walidacja_odrzuca_bledny_email(self):
        with self.assertRaises(kontakt.NiepoprawneDane):
            kontakt.waliduj({
                "name": "Test",
                "email": "nie-email",
                "message": "Tekst",
            })

    @patch.object(kontakt.smtplib, "SMTP", FalszywySMTP)
    def test_wysylka_uzywa_tls_i_reply_to(self):
        kontakt.wyslij({
            "name": "Test",
            "email": "visitor@example.invalid",
            "phone": "",
            "message": "Tekst testowy",
        })
        wiadomosc = FalszywySMTP.ostatnia_wiadomosc
        self.assertEqual(wiadomosc["Reply-To"], "visitor@example.invalid")
        self.assertIn("Tekst testowy", wiadomosc.get_content())

    def _ustaw_tymczasowa_sciezke_smtp(self, **dodatkowe_env) -> Path:
        """kontakt.SMTP_DANE jest liczone raz przy imporcie (jak CENNIK w cennik.py) —
        po zmianie CONTACT_SMTP_SCIEZKA trzeba przeladowac modul, inaczej test i tak
        pisze do domyslnej sciezki sprzed patch.dict."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        sciezka = Path(tmp.name) / "smtp-dane.json"
        patcher = patch.dict(os.environ, {"CONTACT_SMTP_SCIEZKA": str(sciezka), **dodatkowe_env}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        importlib.reload(kontakt)
        self.addCleanup(importlib.reload, kontakt)
        return sciezka

    def test_smtp_dane_z_panelu_maja_pierwszenstwo_przed_zmiennymi(self):
        sciezka = self._ustaw_tymczasowa_sciezke_smtp(
            CONTACT_SMTP_USER="ze-zmiennej@example.invalid",
            CONTACT_SMTP_PASSWORD="haslo-ze-zmiennej",
        )
        self.assertIsNone(kontakt.wczytaj_smtp_dane())
        self.assertEqual(kontakt._smtp_config()["user"], "ze-zmiennej@example.invalid")

        kontakt.zapisz_smtp_dane("z-panelu@example.invalid", "abcd efgh ijkl mnop")
        self.assertTrue(kontakt.smtp_skonfigurowane())
        config = kontakt._smtp_config()
        self.assertEqual(config["user"], "z-panelu@example.invalid")
        self.assertEqual(config["password"], "abcdefghijklmnop")
        self.assertEqual(oct(sciezka.stat().st_mode)[-3:], "600")

    def test_zapisz_smtp_dane_odrzuca_niepoprawny_email(self):
        self._ustaw_tymczasowa_sciezke_smtp()
        with self.assertRaises(kontakt.NiepoprawneDane):
            kontakt.zapisz_smtp_dane("nie-email", "haslo")

    def test_zapisz_smtp_dane_kazdy_zapis_nadpisuje_poprzedni(self):
        self._ustaw_tymczasowa_sciezke_smtp()
        kontakt.zapisz_smtp_dane("pierwszy@example.invalid", "haslo-a")
        kontakt.zapisz_smtp_dane("drugi@example.invalid", "haslo-b")
        dane = kontakt.wczytaj_smtp_dane()
        self.assertEqual(dane["user"], "drugi@example.invalid")
        self.assertEqual(dane["password"], "haslo-b")


if __name__ == "__main__":
    unittest.main()
