# MathML 복구와 이미지 대체

지원하지 않는 원문을 표시하거나 직접 제공한 수식 이미지를 내장합니다.

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
