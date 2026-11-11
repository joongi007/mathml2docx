"""Authored advanced inputs shared by runnable reports and saved-DOCX tests."""

import json
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent / "assets/advanced-math"
CATALOG = json.loads((DIRECTORY / "catalog.json").read_text(encoding="utf-8"))


def source(entry):
    return (DIRECTORY / entry["file"]).read_text(encoding="utf-8").strip()
