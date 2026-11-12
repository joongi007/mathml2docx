# Advanced template workbook

Put the same advanced formulas into existing documents and table cells; combine marker replacement, nested tables, headers, footers, and a landscape page.

## Run

```sh
python -m examples.26_template_workbook
```

[Generated DOCX](../downloads/examples/26_template_workbook.docx)

[Reference PDF](../assets/previews/26_template_workbook.pdf)

## Complete source

```python
"""Advanced equations in existing documents, markers, cells, and nested tables."""

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches

from mathml2docx import MathmlToDocx, TableStyle

from .advanced_math import CATALOG, source
from .support import save

# Use a wider page for block matrices instead of squeezing them into a narrow cell.
document = Document()
section = document.sections[0]
section.page_width = Inches(11.7)
section.page_height = Inches(8.3)
for side in ("left_margin", "right_margin"):
    setattr(section, side, Inches(0.7))
style = document.styles["Normal"]
style.font.name = "Malgun Gothic"
style.element.get_or_add_rPr().get_or_add_rFonts().set(
    qn("w:eastAsia"), "Malgun Gothic"
)
section.header.paragraphs[0].text = "Numerical methods workbook / 수식 검토 기록"
section.footer.paragraphs[0].text = "Inspect, edit, save, and reopen in Word."
document.add_heading("Template workbook / 검토 워크북", 0)
marker = document.add_paragraph("Prepared for {{rea")
marker.add_run("der}}")
parser = MathmlToDocx(
    table_style=TableStyle.GRID,
    stylesheet="* {font-family:'Malgun Gothic'} p,td {font-size:10pt} .review {color:#244488}",
    img_src_base_path=str(Path(__file__).resolve().parent / "assets"),
)
parser.replace_html(document, "{{reader}}", "<b>연구 검토자 / Reviewer</b>")
for entry in (entry for entry in CATALOG if entry["format"] == "mathml"):
    parser.add_html_to_document(
        "<h2>" + entry["id"] + ". " + entry["title"] + "</h2>", document
    )
    cell = document.add_table(rows=1, cols=1).cell(0, 0)
    parser.add_html_to_cell(
        '<p class="review"><b>검토 대상 / Expression</b></p><p>'
        + source(entry)
        + "</p>"
        "<table><tr><th>Check</th><th>Result</th></tr><tr><td>역할·차원</td>"
        "<td><em>Verify every matrix dimension and grouped script.</em></td></tr></table>"
        '<p><a href="https://example.com/workbook">Workbook reference</a> '
        '<img src="swatch.png" width="24"></p>',
        cell,
    )
    parser.add_html_to_document(
        "<ul><li>수식을 클릭하여 편집합니다.</li><li>Save, reopen, and inspect the table.</li></ul>",
        document,
    )
save(document, "26_template_workbook.docx")
```

## Equation input files

- [A01: Normalized Gaussian mixture with nested exponent and radical](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A01.html)
- [A02: Full 3 by 3 Hessian with mixed partial derivatives](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A02.html)
- [A03: Nested block matrix and Schur complement](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A03.html)
- [A04: Three-branch robust loss with radicals and a rational transition](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A04.html)
- [A05: Fourier-Galerkin integral with an embedded infinite sum](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A05.html)
- [A06: Six-level continued fraction with indexed radicals](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A06.html)
- [A07: Euler-Lagrange derivative with a normalized gradient](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A07.html)
- [A08: Tensor contraction with two sums and indexed rational factors](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A08.html)
- [A09: Determinant of a regularized rational 3 by 3 matrix](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A09.html)
- [A10: Generalized quadratic quotient with matrix and transpose](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/A10.html)

[Independent answers (JSON)](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/advanced_math_expectations.json)
