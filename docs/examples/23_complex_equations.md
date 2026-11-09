# 복잡한 수식 갤러리

직접 작성한 MathML 20개와 LaTeX 24개로 중첩 분수·행렬·미분·적분·악센트·수학 글꼴을 비교합니다.

## 실행

```sh
python -m examples.23_complex_equations
```

[생성 DOCX](../downloads/examples/23_complex_equations.docx)

[PDF 참조 결과](../assets/previews/23_complex_equations.pdf)

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

## 화면 비교 시 확인할 점

LibreOffice 7.3 참조 PDF에서 M17 phantom 예약 폭, M19 bevelled 분수, M20 문자열 따옴표는 기대와 다르게 표시됩니다. XML에는 해당 구조·속성·문자가 남아 있지만 화면 동등성 검증을 완료한 항목은 아닙니다. Microsoft Word 직접 확인도 남아 있습니다.

[전체 검증 범위와 한계](../11-validation.md)
