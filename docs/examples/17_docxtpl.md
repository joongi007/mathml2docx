# docxtpl integration

Render a Jinja template and then add HTML paragraphs.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations. This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/17_docxtpl.html">Open HTML preview</a></div><iframe src="../assets/inputs/17_docxtpl.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/17_docxtpl.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/17_docxtpl.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.17_docxtpl
```

[Generated DOCX](../downloads/examples/17_docxtpl.docx)

[Reference PDF](../assets/previews/17_docxtpl.pdf)

## Complete source

```python
"""17 docxtpl example."""

from docx import Document
from docxtpl import DocxTemplate

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "jinja_template.docx"
document = Document()
document.add_paragraph("Hello {{ name }}")
document.save(source)
template = DocxTemplate(source)
template.render({"name": "Alex"})
MathmlToDocx().add_html_to_document(
    "<h2>Added HTML section</h2><p>After Jinja rendering.</p>", template
)
output = OUTPUT / "17_docxtpl.docx"
template.save(output)
print(output)
```
