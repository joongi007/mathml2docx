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
