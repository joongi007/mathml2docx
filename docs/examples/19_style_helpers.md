# Style helpers

Explicitly apply CSS text to a target run or paragraph.

## Compare input and output

This example applies styles directly to Word objects and has no HTML input. Its result is shown in the PDF.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/19_style_helpers.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/19_style_helpers.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.19_style_helpers
```

[Generated DOCX](../downloads/examples/19_style_helpers.docx)

[Reference PDF](../assets/previews/19_style_helpers.pdf)

## Complete source

```python
"""19 style helpers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
paragraph = document.add_paragraph()
run = paragraph.add_run("Explicit targets")
parser = MathmlToDocx()
parser.add_styles_to_run(
    "color:navy;font-weight:bold;text-decoration:underline", run=run
)
parser.add_styles_to_paragraph("margin-left:1cm;text-align:right", paragraph=paragraph)
save(document, "19_style_helpers.docx")
```
