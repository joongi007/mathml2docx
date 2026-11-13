# Inline markers and block replacement

Replace markers spanning formatted runs and insert multiple blocks into cells.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations. This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/15_markers.html">Open HTML preview</a></div><iframe src="../assets/inputs/15_markers.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/15_markers.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/15_markers.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.15_markers
```

[Generated DOCX](../downloads/examples/15_markers.docx)

[Reference PDF](../assets/previews/15_markers.pdf)

## Complete source

```python
"""15 markers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph()
p.add_run("Dear {{na").bold = True
p.add_run("me}}, welcome.").italic = True
cell = document.add_table(1, 1).cell(0, 0)
cell.text = "{{table_content}}"
parser = MathmlToDocx()
parser.replace_html(document, "{{name}}", '<span style="color:teal">Alex</span>')
parser.replace_html(
    document,
    "{{table_content}}",
    "<h2>Inserted blocks</h2><ul><li>First</li><li>Second</li></ul>",
)
save(document, "15_markers.docx")
```
