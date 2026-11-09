"""Paths shared by the runnable examples."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = Path(os.environ.get("MATHML2DOCX_EXAMPLE_OUTPUT", ROOT / "output")).resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)


def save(document, name):
    path = OUTPUT / name
    document.save(path)
    print(path)
    return path
