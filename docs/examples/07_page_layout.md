# Paragraph layout and page breaks

Set alignment, spacing, indentation, line height, and page breaks.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/07_page_layout.html">Open HTML preview</a></div><iframe src="../assets/inputs/07_page_layout.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/07_page_layout.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/07_page_layout.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.07_page_layout
```

[Generated DOCX](../downloads/examples/07_page_layout.docx)

[Reference PDF](../assets/previews/07_page_layout.pdf)

## Complete source

```python
"""07 page layout example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Paragraph layout</h1><p style="text-align:center">Centered</p>
<p style="margin-left:10%;text-indent:12pt;line-height:150%;margin-top:8pt">Indented paragraph with line spacing.</p>
<p style="page-break-after:always">End of page one</p><h2>Page two</h2><p>Continued.</p>""")
save(document, "07_page_layout.docx")
```
