"""02 files unicode example."""

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "unicode.html"
source.write_text(
    "<h1>안녕하세요</h1><p>Índice — 日本語 — Ελληνικά</p>", encoding="utf-8"
)
output = MathmlToDocx().parse_html_file(
    source, OUTPUT / "02_files_unicode.docx", encoding="utf-8"
)
print(output)
