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
    parser.add_argument(
        "--default-math-display", choices=["inline", "block"], default="inline"
    )
    parser.add_argument(
        "--unsupported-math", choices=["error", "text"], default="error"
    )
    parser.add_argument(
        "--math-target", choices=["word", "libreoffice"], default="word"
    )
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must differ")
    if args.output.exists() and not args.force:
        parser.error("output already exists; use --force to replace it")
    converter = MathmlToDocx(
        default_math_display=args.default_math_display,
        unsupported_math=args.unsupported_math,
        math_target=args.math_target,
    )
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
