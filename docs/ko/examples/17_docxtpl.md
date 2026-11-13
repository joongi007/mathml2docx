# docxtpl 연동

Jinja 템플릿을 렌더링한 뒤 HTML 문단을 추가합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.17_docxtpl
```

[생성된 DOCX](../downloads/examples/17_docxtpl.docx)

[참조 PDF](../assets/previews/17_docxtpl.pdf)

## 전체 코드

```python
"""17 docxtpl example."""

from docx import Document
from docxtpl import DocxTemplate

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "jinja_template.docx"
document = Document()
document.add_paragraph("Hello {{ name }}")
document.save(source)
template = DocxTemplate(source)
template.render({"name": "Alex"})
MathmlToDocx().add_html_to_document(
    "<h2>Added HTML section</h2><p>After Jinja rendering.</p>", template
)
output = OUTPUT / "17_docxtpl.docx"
template.save(output)
print(output)
```
