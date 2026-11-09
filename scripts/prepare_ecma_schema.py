"""Fetch pinned official validation schemas into an explicit external directory."""

import argparse
import hashlib
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

ECMA_URL = "https://ecma-international.org/wp-content/uploads/ECMA-376-4_5th_edition_december_2016.zip"
ECMA_SHA256 = "bd25da1109f73762356596918bf5ff8b74a1331642dba5f1c1d1dfc6bed34ecd"
XML_URL = "https://www.w3.org/2001/xml.xsd"
XML_SHA256 = "61960fb3131e38022caad5360e2f33a3382578ab3c80cd58bd74320ede61b20c"


def download(url, digest):
    with urlopen(
        Request(url, headers={"User-Agent": "mathml2docx-validation"}), timeout=60
    ) as response:
        content = response.read(16 * 1024 * 1024 + 1)
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError("Official schema download changed: " + url)
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    target = args.directory.resolve()
    target.mkdir(parents=True, exist_ok=True)
    with ZipFile(BytesIO(download(ECMA_URL, ECMA_SHA256))) as outer:
        with ZipFile(
            BytesIO(outer.read("OfficeOpenXML-XMLSchema-Transitional.zip"))
        ) as schemas:
            for name in schemas.namelist():
                # Extract only flat XSD files; retain the schemas' original bytes.
                if name.endswith(".xsd") and Path(name).name == name:
                    (target / name).write_bytes(schemas.read(name))
    (target / "xml.xsd").write_bytes(download(XML_URL, XML_SHA256))
    print("Prepared official validation schemas:", target)


if __name__ == "__main__":
    main()
