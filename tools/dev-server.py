#!/usr/bin/env python3
"""Lokalny serwer witryny z obsługą projektowej strony 404."""

from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJEKT = Path(__file__).resolve().parent.parent


class ObslugaWitryny(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code != HTTPStatus.NOT_FOUND:
            return super().send_error(code, message, explain)

        plik_404 = PROJEKT / "404.html"
        if not plik_404.is_file():
            return super().send_error(code, message, explain)

        tresc = plik_404.read_bytes()
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(tresc)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(tresc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    handler = partial(ObslugaWitryny, directory=str(PROJEKT))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as serwer:
        print(f"Winnica: http://127.0.0.1:{args.port}")
        try:
            serwer.serve_forever()
        except KeyboardInterrupt:
            print("\nSerwer zatrzymany.")


if __name__ == "__main__":
    main()
