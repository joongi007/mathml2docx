"""Command line file conversion."""

import argparse
from pathlib import Path

from . import MathmlToDocx


def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML, Markdown, MathML or LaTeX to DOCX"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--format", choices=["html", "mathml", "latex", "markdown"], default="html"
    )
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing output"
    )
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must differ")
    if args.output.exists() and not args.force:
        parser.error("output already exists; use --force to replace it")
    converter = MathmlToDocx()
    source = args.input.read_text(encoding=args.encoding)
    document = {
        "html": converter.parse_html_string,
        "mathml": converter.parse_mathml,
        "latex": converter.parse_latex,
        "markdown": converter.parse_markdown,
    }[args.format](source)
    with args.output.open("wb" if args.force else "xb") as output:
        document.save(output)
    print(args.output)


if __name__ == "__main__":
    main()
