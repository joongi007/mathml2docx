# 옵션과 설정 복사

이미지·표·수식·서식을 끄고 설정을 독립적으로 복사합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.18_options
```

[생성된 DOCX](../downloads/examples/18_options.docx)

[참조 PDF](../assets/previews/18_options.pdf)

## 전체 코드

```python
"""18 options example."""

from mathml2docx import MathmlToDocx

from .support import save

source = MathmlToDocx(images=False, tables=False, mathml=False)
parser = MathmlToDocx()
parser.copy_settings_from(source)
parser.options.styles = False
assert parser.get_origin() is parser
html = '<h1>Options</h1><p><b>Plain</b><img src="missing"></p><table><tr><td>Skipped</td></tr></table><math><mi>x</mi></math>'
save(parser.parse_html_string(html), "18_options.docx")
```
