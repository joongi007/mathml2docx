# Word styles and class mapping

Map HTML classes to public style constants and custom character styles.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations. This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/06_word_styles.html">Open HTML preview</a></div><iframe src="../assets/inputs/06_word_styles.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/06_word_styles.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/06_word_styles.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.06_word_styles
```

[Generated DOCX](../downloads/examples/06_word_styles.docx)

[Reference PDF](../assets/previews/06_word_styles.pdf)

## Complete source

```python
"""06 word styles example."""

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import RGBColor

from mathml2docx import MathmlToDocx, ParagraphStyle, TableStyle

from .support import save

document = Document()
style = document.styles.add_style("EmphasisCode", WD_STYLE_TYPE.CHARACTER)
style.font.color.rgb = RGBColor.from_string("7C3AED")
parser = MathmlToDocx(
    paragraph_style=ParagraphStyle.NORMAL,
    table_style=TableStyle.GRID,
    style_map={"p": {"quote": "Quote"}, "span": {"code": "EmphasisCode"}},
)
parser.add_html_to_document(
    '<p class="quote">A quotation with <span class="code">custom character style</span>.</p>',
    document,
)
save(document, "06_word_styles.docx")
```
