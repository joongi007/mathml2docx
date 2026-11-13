# Word styles and class mapping

Map HTML classes to public style constants and custom character styles.

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
