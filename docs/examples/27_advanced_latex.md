# Advanced LaTeX report

Eight distinct advanced LaTeX inputs exercise adjacent matrices, grouped powers, piecewise expressions, nested radicals, sums, and derivatives inside a formatted report.

## Run

```sh
python -m examples.27_advanced_latex
```

[Generated DOCX](../downloads/examples/27_advanced_latex.docx)

[Reference PDF](../assets/previews/27_advanced_latex.pdf)

## Complete source

```python
"""Advanced LaTeX inside a report with prose, tables, and explicit page breaks."""

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from mathml2docx import MathmlToDocx, TableStyle
from mathml2docx.math import latex_to_omml

from .advanced_math import CATALOG, source
from .support import save

document = Document()
document.sections[0].left_margin = Inches(0.65)
document.sections[0].right_margin = Inches(0.65)
normal = document.styles["Normal"]
normal.font.name = "Malgun Gothic"
normal.element.get_or_add_rPr().get_or_add_rFonts().set(
    qn("w:eastAsia"), "Malgun Gothic"
)
parser = MathmlToDocx(
    table_style=TableStyle.GRID,
    stylesheet="* {font-family:'Malgun Gothic'} p,td {font-size:10pt} h2 {color:navy}",
)
parser.add_html_to_document(
    "<h1>Advanced LaTeX / 복합 수식</h1><p>행렬·적분·편미분을 다루는 연구 노트입니다.</p>",
    document,
)
for index, entry in enumerate(entry for entry in CATALOG if entry["format"] == "latex"):
    parser.add_html_to_document(
        "<h2>" + entry["id"] + ". " + entry["title"] + "</h2>", document
    )
    code = document.add_paragraph()
    code.paragraph_format.keep_with_next = True
    code_run = code.add_run(source(entry))
    code_run.font.name = "Consolas"
    code_run.font.size = Pt(9)
    document.add_paragraph()._p.append(latex_to_omml(source(entry)))
    parser.add_html_to_document(
        "<p><strong>검토:</strong> check every matrix boundary, grouped power and radical.</p>"
        "<table><tr><th>Original</th><th>Editable result</th></tr>"
        "<tr><td><i>LaTeX input</i></td><td>Separate numerator and denominator roles.</td></tr></table>"
        '<ol start="2"><li>Click and edit a variable.</li><li>다시 저장한 문서에서도 비교합니다.</li></ol>',
        document,
    )
    if index in {2, 5}:
        document.add_page_break()
save(document, "27_advanced_latex.docx")
```

## Equation input files

- [B01: Nested rational expression with a cubic radical](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B01.tex)
- [B02: Matrix equation with rational and radical coefficients](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B02.tex)
- [B03: Piecewise rational function with an exponential tail](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B03.tex)
- [B04: Block normal equations for constrained least squares](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B04.tex)
- [B05: Double sum with a normalized pairwise distance](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B05.tex)
- [B06: Integral with nested rational and cubic radicals](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B06.tex)
- [B07: Mixed partial derivative with a grouped derivative argument](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B07.tex)
- [B08: Factored rational polynomial with a matrix determinant](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B08.tex)

[Independent answers (JSON)](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/advanced_math_expectations.json)
