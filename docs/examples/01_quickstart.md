# Quick start

Save HTML with one convert() call and receive a Document.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/01_quickstart.html">Open HTML preview</a></div><iframe src="../assets/inputs/01_quickstart.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/01_quickstart.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/01_quickstart.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.01_quickstart
```

[Generated DOCX](../downloads/examples/01_quickstart.docx)

[Reference PDF](../assets/previews/01_quickstart.pdf)

## Complete source

```python
"""01 quickstart example."""

from mathml2docx import convert

from .support import OUTPUT

document = convert(
    "<h1>Hello</h1><p>HTML to editable Word.</p>", OUTPUT / "01_quickstart.docx"
)
print(OUTPUT / "01_quickstart.docx")
```
