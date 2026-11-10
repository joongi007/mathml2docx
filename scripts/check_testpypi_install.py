"""Install the exact wheel served by TestPyPI, with dependencies from PyPI only."""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
from email.parser import BytesParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from zipfile import ZipFile


def expected_distribution(wheel):
    with ZipFile(wheel) as archive:
        metadata_name = next(
            n for n in archive.namelist() if n.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
    if metadata["Name"] != "mathml2docx":
        raise ValueError("Unexpected package in wheel")
    return metadata["Version"], hashlib.sha256(wheel.read_bytes()).hexdigest()


def distribution_url(metadata, version, filename, sha256):
    if metadata["info"]["version"] != version:
        raise ValueError("TestPyPI returned another version")
    for entry in metadata["urls"]:
        if entry["filename"] == filename:
            parsed = urlsplit(entry["url"])
            if (
                entry.get("yanked")
                or entry.get("packagetype") != "bdist_wheel"
                or entry["digests"]["sha256"] != sha256
                or parsed.scheme != "https"
                or parsed.hostname != "test-files.pythonhosted.org"
                or parsed.username is not None
                or parsed.port not in (None, 443)
                or parsed.fragment
            ):
                raise ValueError(
                    "TestPyPI wheel URL/hash does not match the built artifact"
                )
            return entry["url"] + "#sha256=" + sha256
    raise ValueError("Expected wheel is not listed on TestPyPI")


def published_wheel(version, wheel, sha256):
    request = Request(
        f"https://test.pypi.org/pypi/mathml2docx/{version}/json",
        headers={"User-Agent": "mathml2docx-install-check"},
    )
    for attempt in range(24):
        try:
            with urlopen(request, timeout=20) as response:
                metadata = json.load(response)
            return distribution_url(metadata, version, wheel.name, sha256)
        except HTTPError as error:
            if error.code != 404 and error.code < 500:
                raise
        except URLError:
            pass
        if attempt != 23:
            time.sleep(5)
    raise RuntimeError(
        "TestPyPI version did not become available within the retry window"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--python", default="3.14")
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version, sha256 = expected_distribution(args.wheel)
    url = published_wheel(version, args.wheel, sha256)
    with tempfile.TemporaryDirectory(prefix="mathml2docx-testpypi-") as tmp:
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
                "--index-url",
                "https://pypi.org/simple/",
                f"mathml2docx[latex,markdown] @ {url}",
            ],
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-c",
                "import mathml2docx,sys; assert mathml2docx.__version__ == sys.argv[1]",
                version,
            ],
            cwd=tmp,
            check=True,
        )
        subprocess.run(
            [str(python), str(root / "scripts/smoke_distribution.py")],
            cwd=tmp,
            check=True,
        )
    print(
        f"TestPyPI {version}: verified wheel SHA-256 {sha256} and Python {args.python} installation"
    )


if __name__ == "__main__":
    main()
