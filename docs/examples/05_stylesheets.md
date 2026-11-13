# CSS stylesheets

Combine style tags, explicit external CSS loading, selectors, inheritance, and important precedence.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/05_stylesheets.html">Open HTML preview</a></div><iframe src="../assets/inputs/05_stylesheets.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/05_stylesheets.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/05_stylesheets.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.05_stylesheets
```

[Generated DOCX](../downloads/examples/05_stylesheets.docx)

[Reference PDF](../assets/previews/05_stylesheets.pdf)

## Complete source

```python
"""05 stylesheets example."""

from mathml2docx import MathmlToDocx

from .support import save

assets = {
    "theme.css": ".notice {color:teal;font-size:16pt} .notice strong {color:purple}"
}
parser = MathmlToDocx(
    stylesheet_loader=assets.__getitem__, stylesheet="h1 {color:navy}"
)
document = parser.parse_html_string("""<link rel="stylesheet" href="theme.css">
<style>#main {color:red} .notice {color:green !important}</style>
<h1>CSS cascade</h1><p id="main" class="notice" style="color:orange">Important wins. <strong>Nested selector</strong></p>""")
save(document, "05_stylesheets.docx")
```
