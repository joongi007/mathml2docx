"""Install the built wheel in a clean environment and run the public API smoke check."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uv", default="uv")
    parser.add_argument("--python", default="3.14")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    wheels = list((root / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected exactly one built wheel in dist/")
    with tempfile.TemporaryDirectory(prefix="mathml2docx-wheel-check-") as tmp:
        environment = Path(tmp) / "env"
        subprocess.run(
            [args.uv, "venv", "--python", args.python, str(environment)], check=True
        )
        python = environment / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )
        subprocess.run(
            [
                args.uv,
                "pip",
                "install",
                "--python",
                str(python),
                str(wheels[0].resolve()) + "[latex,markdown]",
            ],
            check=True,
        )
        subprocess.run(
            [str(python), str(root / "scripts/smoke_distribution.py")],
            cwd=tmp,
            check=True,
        )


if __name__ == "__main__":
    main()
