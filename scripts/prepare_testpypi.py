"""Assign a unique TestPyPI development version in the temporary CI checkout."""

import argparse
import re
from pathlib import Path

from scripts.check_release import release_version


def prepare_candidate(root, run_id, attempt):
    from packaging.version import Version

    base = release_version(root)
    version = Version(base)
    if version.is_prerelease or version.is_postrelease or version.local:
        raise ValueError(
            "The master version must be the intended final release version"
        )
    if run_id <= 0 or not 1 <= attempt <= 999:
        raise ValueError("Expected a positive run ID and an attempt between 1 and 999")
    candidate = f"{base}.dev{run_id}{attempt:03d}"
    for name, pattern in (
        ("pyproject.toml", r'(?m)^version = "' + re.escape(base) + r'"$'),
        (
            "mathml2docx/__init__.py",
            r'(?m)^__version__ = [\'"]' + re.escape(base) + r'[\'"]$',
        ),
    ):
        path = root / name
        source = path.read_text(encoding="utf-8")
        replacement = "__version__" if name.endswith("__init__.py") else "version"
        content, count = re.subn(pattern, f'{replacement} = "{candidate}"', source)
        if count != 1:
            raise ValueError("Expected one version assignment in " + name)
        path.write_text(content, encoding="utf-8")
    release_version(root)
    return candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--attempt", required=True, type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    candidate = prepare_candidate(
        Path(__file__).resolve().parents[1], args.run_id, args.attempt
    )
    print("TestPyPI candidate:", candidate)
    if args.output:
        with args.output.open("a", encoding="utf-8") as stream:
            stream.write("version=" + candidate + "\n")


if __name__ == "__main__":
    main()
