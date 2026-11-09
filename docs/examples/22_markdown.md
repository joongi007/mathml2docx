# Markdown 연동

제목·표·목록·코드와 ~~취소선~~을 선택 Markdown 프런트엔드로 변환합니다.

## 실행

```sh
python -m examples.22_markdown
```

[생성 DOCX](../downloads/examples/22_markdown.docx)

[PDF 참조 결과](../assets/previews/22_markdown.pdf)

## 전체 코드

```python
"""22 markdown example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install ".[markdown]"
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
