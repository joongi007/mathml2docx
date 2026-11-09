# 목록 번호와 중첩

시작 번호, li의 value, 독립 목록 재시작, 중첩 번호·글머리를 보여 줍니다.

## 실행

```sh
python -m examples.09_lists
```

[생성 DOCX](../downloads/examples/09_lists.docx)

[PDF 참조 결과](../assets/previews/09_lists.pdf)

## 전체 코드

```python
"""09 lists example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1>Lists</h1><ol start="3"><li>Third<ol><li>Nested first</li><li>Nested second</li></ol></li><li value="8">Eighth</li></ol><ol><li>Restart at one</li></ol><ul><li>Bullet<ul><li>Nested bullet</li></ul></li></ul>'
)
save(document, "09_lists.docx")
```
