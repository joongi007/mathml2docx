# 링크와 앵커

외부 링크, 문서 내부 링크, id·name 앵커와 href 없는 링크를 다룹니다.

## 실행

```sh
python -m examples.20_links
```

[생성 DOCX](../downloads/examples/20_links.docx)

[PDF 참조 결과](../assets/previews/20_links.pdf)

## 전체 코드

```python
"""20 links example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1 id="intro">Introduction</h1><p><a href="https://example.com">External link</a> <a href="#intro">Back to introduction</a> <a name="legacy">Named anchor</a> <a>Link without href</a></p>'
)
save(document, "20_links.docx")
```
