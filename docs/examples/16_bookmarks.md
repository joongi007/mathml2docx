# Bookmark replacement

Replace Word bookmark ranges while preserving surrounding content and bookmarks.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations. This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/16_bookmarks.html">Open HTML preview</a></div><iframe src="../assets/inputs/16_bookmarks.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/16_bookmarks.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/16_bookmarks.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.16_bookmarks
```

[Generated DOCX](../downloads/examples/16_bookmarks.docx)

[Reference PDF](../assets/previews/16_bookmarks.pdf)

## Complete source

```python
"""16 bookmarks example."""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph("Before ")
start = OxmlElement("w:bookmarkStart")
start.set(qn("w:id"), "1")
start.set(qn("w:name"), "result")
p._p.append(start)
p.add_run("replace this")
end = OxmlElement("w:bookmarkEnd")
end.set(qn("w:id"), "1")
p._p.append(end)
p.add_run(" after.")
MathmlToDocx().replace_bookmark(document, "result", "<b>new result</b>")
save(document, "16_bookmarks.docx")
```
