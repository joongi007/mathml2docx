# 서식 헬퍼

대상 run과 paragraph에 CSS 문자열을 명시적으로 적용합니다.

## 실행

```sh
python -m examples.19_style_helpers
```

[생성된 DOCX](../downloads/examples/19_style_helpers.docx)

[참조 PDF](../assets/previews/19_style_helpers.pdf)

## 전체 코드

```python
"""19 style helpers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
paragraph = document.add_paragraph()
run = paragraph.add_run("Explicit targets")
parser = MathmlToDocx()
parser.add_styles_to_run(
    "color:navy;font-weight:bold;text-decoration:underline", run=run
)
parser.add_styles_to_paragraph("margin-left:1cm;text-align:right", paragraph=paragraph)
save(document, "19_style_helpers.docx")
```
