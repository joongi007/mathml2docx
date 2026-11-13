# Markdown 연동

제목·표·목록·코드와 ~~취소선~~을 선택 Markdown 프런트엔드로 변환합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.22_markdown
```

[생성된 DOCX](../downloads/examples/22_markdown.docx)

[참조 PDF](../assets/previews/22_markdown.pdf)

## 전체 코드

```python
"""22 markdown example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install "mathml2docx[markdown]"
source = """# Markdown example

1. First
2. Second

| A | B |
|---|---|
| 1 | 2 |

~~Deleted content~~

```python
print('hello')
```
"""
document = MathmlToDocx().parse_markdown(source)
save(document, "22_markdown.docx")
```
