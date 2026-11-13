# MathML 수식

분수·위아래 첨자·n제곱근·울타리·행렬 및 문장 안의 편집 가능한 수식을 생성합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.13_mathml
```

[생성된 DOCX](../downloads/examples/13_mathml.docx)

[참조 PDF](../assets/previews/13_mathml.pdf)

## 전체 코드

```python
"""13 mathml example."""

from mathml2docx import MathmlToDocx

from .support import save

parser = MathmlToDocx()
document = parser.parse_mathml("<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>")
parser.add_html_to_document(
    """<h2>Inline and block math</h2><p>Area:
<math display="inline"><mi>A</mi><mo>=</mo><mi>π</mi><msup><mi>r</mi><mn>2</mn></msup></math>.</p>
<math><mroot><mi>x</mi><mn>3</mn></mroot><mo>+</mo><msubsup><mi>x</mi><mn>1</mn><mn>2</mn></msubsup></math>
<math><mfenced open="[" close="]"><mtable><mtr><mtd><mn>1</mn></mtd><mtd><mn>2</mn></mtd></mtr><mtr><mtd><mn>3</mn></mtd><mtd><mn>4</mn></mtd></mtr></mtable></mfenced></math>""",
    document,
)
save(document, "13_mathml.docx")
```
