# Word 스타일과 클래스 매핑

공개 스타일 Enum과 사용자 정의 character style을 HTML class에 연결합니다.

## 실행

```sh
python -m examples.06_word_styles
```

[생성 DOCX](../downloads/examples/06_word_styles.docx)

[PDF 참조 결과](../assets/previews/06_word_styles.pdf)

## 전체 코드

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
