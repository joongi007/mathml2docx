# Files, encoding, and Unicode

Use UTF-8 input, Korean/Japanese/accented text, and exact output extensions.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/02_files_unicode.html">Open HTML preview</a></div><iframe src="../assets/inputs/02_files_unicode.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/02_files_unicode.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/02_files_unicode.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

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
