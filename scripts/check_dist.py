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
            if any(name.lower().endswith(".docx") for name in names):
                raise RuntimeError("Generated DOCX must not be bundled: " + str(wheel))
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
            if any(name.lower().endswith(".docx") for name in names):
                raise RuntimeError("Generated DOCX must not be bundled: " + str(source))
            for required in [
                "examples/assets/math-corpus/catalog.json",
                "examples/assets/mixed_math.html",
                "tests/fixtures/math_expectations.json",
                "tests/fixtures/mixed_math_expectation.json",
                "tests/docx_oracle.py",
                "tests/test_docx_oracles.py",
                "README.ko.md",
                "mkdocs.ko.yml",
                "docs/ko/index.md",
                "docs_theme/main.html",
                "docs_theme/ko.json",
                "scripts/docs_hooks.py",
                "examples/catalog.ko.json",
            ]:
                if not any(name.endswith("/" + required) for name in names):
                    raise RuntimeError(
                        "DOCX oracle source missing from sdist: " + required
                    )
            for notice in notices:
                if not any(name.endswith("/" + notice) for name in names):
                    raise RuntimeError("License file missing from sdist: " + notice)
    print(
        "Distribution checks passed: Python >=3.6, MIT/notices, oracle sources, no XSL/generated DOCX files"
    )


if __name__ == "__main__":
    main()
