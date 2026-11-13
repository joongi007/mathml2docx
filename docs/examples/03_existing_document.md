# Existing documents and cells

Append content to a Document and insert HTML into table cells.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations. This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/03_existing_document.html">Open HTML preview</a></div><iframe src="../assets/inputs/03_existing_document.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/03_existing_document.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/03_existing_document.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.03_existing_document
```

[Generated DOCX](../downloads/examples/03_existing_document.docx)

[Reference PDF](../assets/previews/03_existing_document.pdf)

## Complete source

```python
"""03 existing document example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
document.add_paragraph("Existing introduction")
parser = MathmlToDocx()
parser.add_html_to_document(
    "<h2>Added HTML</h2><p>Append without replacing existing content.</p>", document
)
cell = document.add_table(1, 1).cell(0, 0)
parser.add_html_to_cell("<b>HTML in a cell</b><br>Second line", cell)
save(document, "03_existing_document.docx")
```
