# 고급 LaTeX 보고서

서로 다른 LaTeX 수식 8개로 연속 행렬·괄호 지수·조각함수·중첩 근호·합·편미분을 서식이 있는 보고서에서 검사합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다. 이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/27_advanced_latex.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/27_advanced_latex.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/27_advanced_latex.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/27_advanced_latex.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.27_advanced_latex
```

[생성된 DOCX](../downloads/examples/27_advanced_latex.docx)

[참조 PDF](../assets/previews/27_advanced_latex.pdf)

## 전체 코드

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

## 수식 입력 파일

- [B01: Nested rational expression with a cubic radical](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B01.tex)
- [B02: Matrix equation with rational and radical coefficients](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B02.tex)
- [B03: Piecewise rational function with an exponential tail](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B03.tex)
- [B04: Block normal equations for constrained least squares](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B04.tex)
- [B05: Double sum with a normalized pairwise distance](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B05.tex)
- [B06: Integral with nested rational and cubic radicals](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B06.tex)
- [B07: Mixed partial derivative with a grouped derivative argument](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B07.tex)
- [B08: Factored rational polynomial with a matrix determinant](https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/B08.tex)

[독립 정답 (JSON)](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/advanced_math_expectations.json)
