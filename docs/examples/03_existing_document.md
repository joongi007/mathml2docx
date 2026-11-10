# Existing documents and cells

Append content to a Document and insert HTML into table cells.

## Run

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
