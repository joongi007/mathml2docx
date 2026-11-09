"""Convert UTF-8 HTML to an exact DOCX path without overwriting existing files."""

import argparse
from pathlib import Path

from mathml2docx import MathmlToDocx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--images", action="store_true", help="Enable image loading")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"output already exists: {args.output}")
    html = args.input.read_text(encoding="utf-8")
    document = MathmlToDocx(images=args.images).parse_html_string(html)
    with args.output.open("xb") as output:
        document.save(output)
    print(args.output)


if __name__ == "__main__":
    main()
