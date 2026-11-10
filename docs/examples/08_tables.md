# Merged and nested tables

Combine table sections, row/column spans, cell backgrounds, width, borders, and nesting.

## Run

```sh
python -m examples.08_tables
```

[Generated DOCX](../downloads/examples/08_tables.docx)

[Reference PDF](../assets/previews/08_tables.pdf)

## Complete source

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
