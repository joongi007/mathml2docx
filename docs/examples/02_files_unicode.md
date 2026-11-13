# Files, encoding, and Unicode

Use UTF-8 input, Korean/Japanese/accented text, and exact output extensions.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.02_files_unicode
```

[Generated DOCX](../downloads/examples/02_files_unicode.docx)

[Reference PDF](../assets/previews/02_files_unicode.pdf)

## Complete source

```python
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
```
