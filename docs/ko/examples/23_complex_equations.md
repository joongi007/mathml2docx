# 복잡한 수식 갤러리

직접 작성한 MathML 20개와 LaTeX 24개로 중첩 분수·행렬·미분·적분·악센트·수학 글꼴을 비교합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다. 이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/23_complex_equations.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/23_complex_equations.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/23_complex_equations.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/23_complex_equations.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.23_complex_equations
```

[생성된 DOCX](../downloads/examples/23_complex_equations.docx)

[참조 PDF](../assets/previews/23_complex_equations.pdf)

## 전체 코드

```python
"""Complex equations for inspection in Word and independent renderers."""

from docx import Document

from mathml2docx import mathml_to_omml
from mathml2docx.math import latex_to_omml

from .math_corpus import LATEX, SHOWCASE
from .support import save

document = Document()
document.add_heading("Complex equation gallery", 0)
document.add_paragraph(
    "Original examples: inspect fraction bars, script roles, radicals, accents, matrices and mathematical alphabets."
)
for index, (name, body) in enumerate(SHOWCASE, 1):
    document.add_heading(f"M{index:02d}: {name}", 2)
    document.add_paragraph()._p.append(mathml_to_omml("<math>" + body + "</math>"))
document.add_page_break()
document.add_heading("LaTeX frontend", 1)
for index, source in enumerate(LATEX, 1):
    document.add_heading(f"L{index:02d}", 2)
    document.add_paragraph(source).paragraph_format.keep_with_next = True
    document.add_paragraph()._p.append(latex_to_omml(source))
save(document, "23_complex_equations.docx")
```

## 화면 비교 시 참고할 점

phantom의 예약 공간, 기울어진 분수, 문자열 따옴표 등은 Word와 LibreOffice에서 다르게 표시될 수 있습니다. 이런 세부 표현이 중요하면 입력과 생성된 문서를 함께 비교하세요.

[검증 범위와 한계](../11-validation.md)
