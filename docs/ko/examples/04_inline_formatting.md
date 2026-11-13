# 글자 서식과 색상

굵기·기울임·밑줄·취소선·위아래 첨자·코드·반투명 색상 합성을 보여 줍니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.04_inline_formatting
```

[생성된 DOCX](../downloads/examples/04_inline_formatting.docx)

[참조 PDF](../assets/previews/04_inline_formatting.pdf)

## 전체 코드

```python
"""04 inline formatting example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Inline formatting</h1><p><b>Bold</b> <i>italic</i> <u>underline</u>
<del>removed</del> H<sub>2</sub>O x<sup>2</sup> <code>code()</code></p>
<p style="font-family:DejaVu Sans;font-size:14pt;color:navy">Named color and font</p>
<p style="background-color:blue"><span style="background-color:rgba(255,0,0,.5)">Purple blend</span></p>
<pre>first\tsecond\n  indented code</pre>""")
save(document, "04_inline_formatting.docx")
```
