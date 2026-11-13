# 고급 수식 연구 보고서

서로 다른 고급 MathML 수식 10개를 한영 본문·병합/중첩 표·목록·이미지·링크·페이지 나누기와 결합합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/25_research_report.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/25_research_report.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/25_research_report.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/25_research_report.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.25_research_report
```

[생성된 DOCX](../downloads/examples/25_research_report.docx)

[참조 PDF](../assets/previews/25_research_report.pdf)

## 전체 코드

```python
"""Distinct advanced MathML formulas inside a bilingual research-style report."""

from pathlib import Path

from mathml2docx import TableStyle, convert

from .advanced_math import CATALOG, source
from .support import save

sections = [
    """<style>
body {font-family:'Malgun Gothic';font-size:10pt;color:#1e293b}
h1,h2 {color:#17365d} h1 {font-size:20pt} h2 {font-size:14pt} .equation {text-align:center;margin-top:12pt;margin-bottom:12pt}
.note {background-color:#eef2ff} th {background-color:#dbeafe}
</style><h1>Advanced numerical methods / 고급 수치 해석</h1>
<p class="note">한글 설명과 mathematical notation in one report. These methods combine probability, matrix analysis and variational calculus.</p>
<p><b>Methods:</b> normalized models, matrix identities and differential equations. <a href="https://example.com/methods">Method reference</a>.</p>"""
]
for index, entry in enumerate(e for e in CATALOG if e["format"] == "mathml"):
    sections.extend(
        [
            f"<h2>{entry['id']}. {entry['title']}</h2>",
            "<p><strong>가정과 해석:</strong> the expression below keeps each numerator, "
            "denominator, matrix cell and script editable. <em>Check the grouped arguments.</em></p>",
            '<p class="equation">' + source(entry) + "</p>",
            '<ol start="3"><li>분자·분모와 첨자의 역할을 확인합니다.</li>'
            "<li>Compare the expression with the original text input.</li></ol>",
        ]
    )
    if index % 2 == 0:
        sections.append(
            '<table><tr><th colspan="2">검토 기록 / Review record</th></tr>'
            '<tr><td rowspan="2">Assumptions</td><td><b>Finite dimensions</b> and positive parameters.</td></tr>'
            "<tr><td><table><tr><td>Nested note</td><td><i>Preserve the original cell order.</i></td></tr></table></td></tr>"
            '</table><p><img src="swatch.png" width="48"> <u>Reference swatch</u> and a caption.</p>'
        )
    if index in {2, 5, 8}:
        sections.append(
            '<p style="page-break-after:always">Section review complete.</p>'
        )
document = convert(
    "<html><body>" + "".join(sections) + "</body></html>",
    table_style=TableStyle.GRID,
    img_src_base_path=str(Path(__file__).resolve().parent / "assets"),
)
save(document, "25_research_report.docx")
```

## 수식 입력 파일

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

[독립 정답 (JSON)](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/advanced_math_expectations.json)
