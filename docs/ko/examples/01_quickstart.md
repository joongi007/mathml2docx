# 빠른 시작

convert() 한 번으로 HTML을 저장하고 Document를 반환받습니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.01_quickstart
```

[생성된 DOCX](../downloads/examples/01_quickstart.docx)

[참조 PDF](../assets/previews/01_quickstart.pdf)

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
