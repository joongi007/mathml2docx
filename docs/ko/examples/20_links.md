# 링크와 앵커

외부 링크, 문서 내부 링크, id·name 앵커와 href 없는 링크를 다룹니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.20_links
```

[생성된 DOCX](../downloads/examples/20_links.docx)

[참조 PDF](../assets/previews/20_links.pdf)

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
