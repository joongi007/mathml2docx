# Equation-heavy mixed report

Combine 120 equation placements with merged/nested tables, lists, images, links, multilingual text, and page breaks.

## Run

```sh
python -m examples.24_dense_report
```

[Generated DOCX](../downloads/examples/24_dense_report.docx)

[Reference PDF](../assets/previews/24_dense_report.pdf)

## Complete source

```python
"""A paginated report combining 120 equations and repeated HTML structures."""

from pathlib import Path

from mathml2docx import convert

from .math_corpus import SHOWCASE
from .support import save

blocks = [
    "<style>h1 {color:navy} td {background-color:#eef2ff} .label {font-weight:bold;color:#244488}</style><h1>Mixed mathematical report</h1>"
]
for section in range(5):
    blocks.append(
        f"<h2>Section {section + 1}</h2><p>한글 설명과 mathematical notation in one report.</p>"
    )
    for index, (name, body) in enumerate(SHOWCASE):
        blocks.append(
            f'<p><span class="label">{section + 1}.{index + 1} {name}</span> — before <math display="inline">{body}</math> after <i>formatted explanation</i>.</p>'
        )
        if index % 5 == 0:
            blocks.append(
                '<table><tr><th>Context</th><th>Equation and formatting</th></tr><tr><td rowspan="2">Merged cell</td><td><b>Ratio</b>: <math display="inline"><mfrac><mi>a</mi><mi>b</mi></mfrac></math></td></tr><tr><td><table><tr><td>Nested table</td></tr></table></td></tr></table><ol start="3"><li>Check the numerator and denominator.</li><li>Keep <strong>bold</strong> and <em>italic</em> text.</li></ol><p><a href="https://example.com">Reference link</a> <img src="swatch.png" width="32"> Caption.</p>'
            )
    if section < 4:
        blocks.append('<p style="page-break-after:always">End of section.</p>')
document = convert(
    "".join(blocks), img_src_base_path=str(Path(__file__).resolve().parent / "assets")
)
save(document, "24_dense_report.docx")
```
