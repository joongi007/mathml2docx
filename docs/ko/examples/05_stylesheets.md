# CSS 스타일시트

style 태그, 외부 CSS 로더, 선택자·상속·important 우선순위를 함께 사용합니다.

## 실행

```sh
python -m examples.05_stylesheets
```

[생성된 DOCX](../downloads/examples/05_stylesheets.docx)

[참조 PDF](../assets/previews/05_stylesheets.pdf)

## 전체 코드

```python
"""05 stylesheets example."""

from mathml2docx import MathmlToDocx

from .support import save

assets = {
    "theme.css": ".notice {color:teal;font-size:16pt} .notice strong {color:purple}"
}
parser = MathmlToDocx(
    stylesheet_loader=assets.__getitem__, stylesheet="h1 {color:navy}"
)
document = parser.parse_html_string("""<link rel="stylesheet" href="theme.css">
<style>#main {color:red} .notice {color:green !important}</style>
<h1>CSS cascade</h1><p id="main" class="notice" style="color:orange">Important wins. <strong>Nested selector</strong></p>""")
save(document, "05_stylesheets.docx")
```
