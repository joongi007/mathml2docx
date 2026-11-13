# Merged and nested tables

Combine table sections, row/column spans, cell backgrounds, width, borders, and nesting.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/08_tables.html">Open HTML preview</a></div><iframe src="../assets/inputs/08_tables.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/08_tables.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/08_tables.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.08_tables
```

[Generated DOCX](../downloads/examples/08_tables.docx)

[Reference PDF](../assets/previews/08_tables.pdf)

## Complete source

```python
"""08 tables example."""

from mathml2docx import TableStyle, convert

from .support import save

document = convert(
    """<style>th {background-color:navy;color:white} td {font-size:11pt}</style>
<table style="width:100%;border:1px solid navy"><thead><tr><th colspan="2">Merged header</th></tr></thead>
<tbody><tr><td rowspan="2">Two rows</td><td>A</td></tr><tr><td>B</td></tr>
<tr><td>Nested<table><tr><td>Inner cell</td></tr></table></td><td></td></tr></tbody></table>""",
    table_style=TableStyle.GRID,
)
save(document, "08_tables.docx")
```
