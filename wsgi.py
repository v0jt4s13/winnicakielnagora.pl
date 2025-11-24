from pathlib import Path
from flask import Flask, send_from_directory

BASE = Path(__file__).parent
STATIC_CANDIDATES = [BASE / "dist" / "public", BASE]  # wybierz dist/public po buildzie, inaczej katalog repo
STATIC_ROOT = next((p for p in STATIC_CANDIDATES if p.exists()), BASE)

app = Flask(__name__, static_folder=str(STATIC_ROOT), static_url_path="")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str):
    target = STATIC_ROOT / path
    if target.is_file():
        return send_from_directory(STATIC_ROOT, path)
    return send_from_directory(STATIC_ROOT, "index.html")
