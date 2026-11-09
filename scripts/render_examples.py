"""Render generated DOCX examples with an installed LibreOffice executable."""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soffice", default=shutil.which("soffice"))
    parser.add_argument("--input", type=Path, default=Path("examples/output"))
    parser.add_argument("--output", type=Path, default=Path("examples/output/pdf"))
    args = parser.parse_args()
    if not args.soffice:
        parser.error("Install LibreOffice or supply --soffice PATH")
    files = sorted(args.input.glob("[0-9][0-9]_*.docx"))
    if not files:
        parser.error("No examples found; run python -m examples.run_all first")
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mathml2docx-render-") as tmp:
        subprocess.run(
            [
                args.soffice,
                "-env:UserInstallation=" + Path(tmp).as_uri(),
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(args.output.resolve()),
                *[str(path.resolve()) for path in files],
            ],
            check=True,
            timeout=120,
        )
    missing = [
        path.stem
        for path in files
        if not (args.output / (path.stem + ".pdf")).is_file()
    ]
    if missing:
        raise RuntimeError("Rendering did not produce PDFs: " + ", ".join(missing))
    print("Rendered", len(files), "PDFs to", args.output)


if __name__ == "__main__":
    main()
