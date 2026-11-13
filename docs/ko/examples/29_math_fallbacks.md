# MathML 복구와 이미지 대체

지원하지 않는 원문을 표시하거나 직접 제공한 수식 이미지를 내장합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/29_math_fallbacks.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/29_math_fallbacks.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/29_math_fallbacks.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/29_math_fallbacks.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.29_math_fallbacks
```

[생성된 DOCX](../downloads/examples/29_math_fallbacks.docx)

[참조 PDF](../assets/previews/29_math_fallbacks.pdf)

## 전체 코드

```python
"""Explicit recovery: preserve MathML source or embed a known rendered image."""

from pathlib import Path

from mathml2docx import MathmlToDocx

from .support import save

# This sample ships two pre-rendered expressions. Replace this lookup with your
# own trusted renderer to handle other notations; do not substitute an unrelated image.
BOXED_X = (
    '<math alttext="boxed x"><menclose notation="box"><mi>x</mi></menclose></math>'
)
CIRCLED_X = (
    '<math alttext="circled x"><menclose notation="circle"><mi>x</mi></menclose></math>'
)


def fallback(source, error):
    if source == CIRCLED_X:
        return (Path(__file__).parent / "assets/circled-x.png").read_bytes()
    if source == BOXED_X:
        return (Path(__file__).parent / "assets/boxed-x.png").read_bytes()
    return "[Unconverted MathML] " + source


parser = MathmlToDocx(math_target="libreoffice", mathml_fallback=fallback)
document = parser.convert(
    "<h1>Recovering unsupported notation</h1><p>The following circled x is an image: "
    + CIRCLED_X
    + ".</p>"
)
parser.add_html_to_document(
    "<p>A boxed x uses the same explicit recovery: " + BOXED_X + ".</p>", document
)
parser.add_html_to_document(
    "<p>Unrecognized input remains visible as source:</p><math><unknown><mi>y</mi></unknown></math>",
    document,
)
save(document, "29_math_fallbacks.docx")
```
