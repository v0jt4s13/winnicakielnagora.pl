"""Gallery for 'O nas' section — read, validate and save `data/o_nas_galeria.json`.

Common module for two entry points:
  * `tools/panel/serwer.py` — panel run locally,
  * `wsgi.py` — panel on production, behind password.

This ensures both paths validate data the same way. Module has no knowledge of HTTP
and serves nothing — data only.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ASSETS = PROJECT / "assets" / "o_nas_galeria"

# Starter version, versioned in repository. On production serves only to seed
# the working file on first run.
GALLERY_IN_REPO = PROJECT / "data" / "o_nas_galeria.json"

# Live gallery. On production point it OUTSIDE the deployment directory (GALLERY_PATH env var),
# so the next deploy doesn't overwrite user's images. Locally stays in repo file.
GALLERY = Path(os.environ.get("GALLERY_PATH") or GALLERY_IN_REPO).expanduser()
BACKUP = GALLERY.with_suffix(GALLERY.suffix + ".bak")
# Exclusively for serialization in save_safely() — see there. Empty file, content irrelevant.
LOCK = GALLERY.with_suffix(GALLERY.suffix + ".lock")


def ensure_file() -> None:
  """On first run, copies version from repo to working path.

  Without this, panel on a fresh server would start with an empty gallery,
  even though repo has a ready list.
  """
  if GALLERY.exists() or GALLERY == GALLERY_IN_REPO:
    return
  GALLERY.parent.mkdir(parents=True, exist_ok=True)
  if GALLERY_IN_REPO.exists():
    GALLERY.write_bytes(GALLERY_IN_REPO.read_bytes())


SKELETON = {"gallery": []}
FILE_PERMISSIONS = 0o640


def load() -> dict:
  """Returns gallery data. Missing file → skeleton, but doesn't create it."""
  if not GALLERY.exists():
    return dict(SKELETON)
  return json.loads(GALLERY.read_text(encoding="utf-8"))


def _error(index, field, message) -> dict:
  return {"index": index, "field": field, "message": message}


def validate(data) -> list[dict]:
  """List of errors; empty means data is ready to save.

  Server is the arbiter — even locally, we don't trust the browser.
  """
  errors: list[dict] = []

  if not isinstance(data, dict):
    return [_error(None, None, "Expected JSON object")]

  gallery = data.get("gallery")
  if not isinstance(gallery, list):
    return [_error(None, "gallery", "Gallery must be an array")]

  seen_order: set[int] = set()
  assets_path = ASSETS.resolve() if ASSETS.exists() else None

  for i, item in enumerate(gallery):
    if not isinstance(item, dict):
      errors.append(_error(i, None, "Item must be an object"))
      continue

    # Validate required fields
    for field in ("path", "title", "alt", "order", "active"):
      if field not in item:
        errors.append(_error(i, field, "Required field"))

    # Validate path
    path = item.get("path", "")
    if not isinstance(path, str) or not path.strip():
      errors.append(_error(i, "path", "Path must be a non-empty string"))
    # Note: files can be from main gallery (butelki/...) or custom folder
    # Don't validate file existence here — gallery is read-only from website perspective

    # Validate title (can be empty)
    title = item.get("title", "")
    if not isinstance(title, str):
      errors.append(_error(i, "title", "Title must be a string"))

    # Validate alt
    alt = item.get("alt", "")
    if not isinstance(alt, str) or not alt.strip():
      errors.append(_error(i, "alt", "Alt text must be a non-empty string"))

    # Validate order
    order = item.get("order")
    if not isinstance(order, int) or order < 1:
      errors.append(_error(i, "order", "Order must be a positive integer"))
    elif order in seen_order:
      errors.append(_error(i, "order", f"Duplicate order: {order}"))
    else:
      seen_order.add(order)

    # Validate active
    active = item.get("active")
    if not isinstance(active, bool):
      errors.append(_error(i, "active", "Active must be true or false"))

    # Check for unknown fields
    allowed = {"path", "title", "alt", "order", "active"}
    for field in item:
      if field not in allowed:
        errors.append(_error(i, field, f"Unknown field: {field}"))

  return errors


def version_hash() -> str:
  """Hash of current file for conflict detection."""
  if not GALLERY.exists():
    return "0"
  return hashlib.sha256(GALLERY.read_bytes()).hexdigest()


def save(data: dict) -> None:
  """Write gallery JSON to disk (atomic). Creates .bak backup."""
  GALLERY.parent.mkdir(parents=True, exist_ok=True)
  GALLERY.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
  )
  GALLERY.chmod(FILE_PERMISSIONS)
  # Backup
  import shutil
  shutil.copy2(GALLERY, BACKUP)


class SaveConflict(Exception):
  """File was modified since we loaded it."""

  def __init__(self, current_version: str, diffs: list):
    self.current_version = current_version
    self.diffs = diffs
    super().__init__()


def save_safely(data: dict, base_version: str, base_data: dict | None = None) -> str:
  """Like save(), but rejects write if file changed since `base_version`.

  No database or document versioning — comparing file hash is the simplest
  robust substitute. Without this, two editors would overwrite each other silently,
  since save() always replaces the entire file, not just one item.

  Checking version and writing are under a single lock (fcntl) — without it,
  two nearly-simultaneous writes could both pass the check before either writes
  (tools/panel/serwer.py handles tasks in separate threads).
  """
  LOCK.parent.mkdir(parents=True, exist_ok=True)
  with open(LOCK, "a") as lock_handle:
    fcntl.flock(lock_handle, fcntl.LOCK_EX)
    current = version_hash()
    if base_version != current:
      diffs = _summarize_diffs(base_data, load()) if isinstance(base_data, dict) else []
      raise SaveConflict(current, diffs)
    save(data)
    return version_hash()


def _summarize_diffs(old_data, new_data) -> list[dict]:
  """Simple diff: which items changed (for UI display)."""
  if not isinstance(old_data, dict) or not isinstance(new_data, dict):
    return []
  old_items = {str(i.get("order", i)): i for i in old_data.get("gallery", [])}
  new_items = {str(i.get("order", i)): i for i in new_data.get("gallery", [])}
  changes = []
  for order in set(list(old_items.keys()) + list(new_items.keys())):
    if old_items.get(order) != new_items.get(order):
      changes.append({"order": order, "changed": True})
  return changes


def initial_state() -> dict:
  """Data that panel needs on startup."""
  ensure_file()
  data = load()
  return {
    "gallery": data.get("gallery", []),
    "version": version_hash(),
  }


def backup_info() -> str:
  """Path to backup file for UI display.

  When gallery lives outside project dir (GALLERY_PATH on production),
  `relative_to` raises ValueError — return full path instead to avoid
  crashing after successful save.
  """
  try:
    return str(BACKUP.relative_to(PROJECT))
  except ValueError:
    return str(BACKUP)


def delete_image(image_path: str) -> None:
  """Delete image from o_nas folder if it exists.

  Args:
    image_path: Relative path like "o_nas_galeria/image.jpg"
  """
  if not isinstance(image_path, str) or "/" not in image_path:
    return

  # Only delete images from o_nas_galeria folder, not from main gallery
  if not image_path.startswith("o_nas_galeria/"):
    return

  image_file = ASSETS / image_path.replace("o_nas_galeria/", "")
  if image_file.exists() and image_file.is_file():
    try:
      image_file.unlink()
    except OSError:
      pass


def copy_image_with_suffix(source_path: str) -> str:
  """Copy image from main gallery to o_nas folder with suffix if duplicate.

  Args:
    source_path: Relative path from attached_assets/ (e.g., "photos/butelki/image.jpg")

  Returns:
    Relative path under attached_assets/ (e.g., "o_nas_galeria/image.jpg")

  Raises:
    FileNotFoundError: Source file doesn't exist
    IOError: Cannot create destination directory or copy fails
  """
  import shutil

  source = PROJECT / "attached_assets" / source_path
  if not source.exists():
    raise FileNotFoundError(f"Source image not found: {source_path}")

  ASSETS.mkdir(parents=True, exist_ok=True)

  filename = source.name
  dest = ASSETS / filename

  # Add suffix if file exists
  if dest.exists():
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
      stem, ext = parts
      counter = 1
      while True:
        new_filename = f"{stem}_{counter}.{ext}"
        dest = ASSETS / new_filename
        if not dest.exists():
          break
        counter += 1
    else:
      stem = filename
      counter = 1
      while True:
        new_filename = f"{stem}_{counter}"
        dest = ASSETS / new_filename
        if not dest.exists():
          break
        counter += 1

  shutil.copy2(source, dest)
  dest.chmod(FILE_PERMISSIONS)

  return f"assets/o_nas_galeria/{dest.name}"