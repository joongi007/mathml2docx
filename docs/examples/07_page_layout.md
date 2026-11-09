# 문단 배치와 페이지 나누기

정렬·여백·들여쓰기·줄 간격과 페이지 나누기를 지정합니다.

## 실행

```sh
python -m examples.07_page_layout
```

[생성 DOCX](../downloads/examples/07_page_layout.docx)

[PDF 참조 결과](../assets/previews/07_page_layout.pdf)

## 전체 코드

```python
"""07 page layout example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Paragraph layout</h1><p style="text-align:center">Centered</p>
<p style="margin-left:10%;text-indent:12pt;line-height:150%;margin-top:8pt">Indented paragraph with line spacing.</p>
<p style="page-break-after:always">End of page one</p><h2>Page two</h2><p>Continued.</p>""")
save(document, "07_page_layout.docx")
```
