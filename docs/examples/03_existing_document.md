# 기존 문서와 표 셀

기존 Document에 내용을 추가하고 셀 안에 HTML을 삽입합니다.

## 실행

```sh
python -m examples.03_existing_document
```

[생성 DOCX](../downloads/examples/03_existing_document.docx)

[PDF 참조 결과](../assets/previews/03_existing_document.pdf)

## 전체 코드

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
