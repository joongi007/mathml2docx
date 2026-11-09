# 빠른 시작

convert() 한 번으로 HTML을 저장하고 Document를 반환받습니다.

## 실행

```sh
python -m examples.01_quickstart
```

[생성 DOCX](../downloads/examples/01_quickstart.docx)

[PDF 참조 결과](../assets/previews/01_quickstart.pdf)

## 전체 코드

```python
"""01 quickstart example."""

from mathml2docx import convert

from .support import OUTPUT

document = convert(
    "<h1>Hello</h1><p>HTML to editable Word.</p>", OUTPUT / "01_quickstart.docx"
)
print(OUTPUT / "01_quickstart.docx")
```
