# 표 병합과 중첩

thead·tbody, rowspan·colspan, 셀 배경, 표 폭·테두리와 중첩 표를 조합합니다.

## 실행

```sh
python -m examples.08_tables
```

[생성 DOCX](../downloads/examples/08_tables.docx)

[PDF 참조 결과](../assets/previews/08_tables.pdf)

## 전체 코드

```python
"""08 tables example."""

from mathml2docx import TableStyle, convert

from .support import save

document = convert(
    """<style>th {background-color:navy;color:white} td {font-size:11pt}</style>
<table style="width:100%;border:1px solid navy"><thead><tr><th colspan="2">Merged header</th></tr></thead>
<tbody><tr><td rowspan="2">Two rows</td><td>A</td></tr><tr><td>B</td></tr>
<tr><td>Nested<table><tr><td>Inner cell</td></tr></table></td><td></td></tr></tbody></table>""",
    table_style=TableStyle.GRID,
)
save(document, "08_tables.docx")
```
