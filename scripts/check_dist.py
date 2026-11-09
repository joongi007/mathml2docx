"""Verify the current distribution's Python/license metadata and XSL exclusion."""

import tarfile
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def main():
    wheels = sorted(Path("dist").glob("*.whl"))
    sources = sorted(Path("dist").glob("*.tar.gz"))
    if not wheels or not sources:
        raise RuntimeError("Build both wheel and source distribution first")
    notices = {"LICENSE", "THIRD_PARTY_NOTICES.md"}
    for wheel in wheels:
        with ZipFile(wheel) as archive:
            names = archive.namelist()
            if any(name.lower().endswith((".xsl", ".xslt")) for name in names):
                raise RuntimeError("Unexpected stylesheet in " + str(wheel))
            metadata_name = next(
                name for name in names if name.endswith(".dist-info/METADATA")
            )
            metadata = BytesParser().parsebytes(archive.read(metadata_name))
            if metadata.get("License-Expression") != "MIT":
                raise RuntimeError("Unexpected project license expression")
            if metadata.get("Requires-Python") != ">=3.6":
                raise RuntimeError("Python 3.6 support metadata is missing")
            if not notices.issubset(set(metadata.get_all("License-File", []))):
                raise RuntimeError("License notices missing from wheel metadata")
            for notice in notices:
                if not any(
                    name.endswith(".dist-info/licenses/" + notice) for name in names
                ):
                    raise RuntimeError("License file missing from wheel: " + notice)
    for source in sources:
        with tarfile.open(source) as archive:
            names = archive.getnames()
            if any(name.lower().endswith((".xsl", ".xslt")) for name in names):
                raise RuntimeError("Unexpected stylesheet in " + str(source))
            for notice in notices:
                if not any(name.endswith("/" + notice) for name in names):
                    raise RuntimeError("License file missing from sdist: " + notice)
    print("Distribution checks passed: Python >=3.6, MIT/notices, no XSL files")


if __name__ == "__main__":
    main()
