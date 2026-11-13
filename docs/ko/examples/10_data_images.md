# 인라인 base64 이미지

data URL 이미지를 글자 사이에 삽입하고 표시 폭을 지정합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.10_data_images
```

[생성된 DOCX](../downloads/examples/10_data_images.docx)

[참조 PDF](../assets/previews/10_data_images.pdf)

## 전체 코드

```python
"""10 data images example."""

import base64

from mathml2docx import convert

from .support import ROOT, save

encoded = base64.b64encode((ROOT / "assets/swatch.png").read_bytes()).decode()
document = convert(
    '<p>Before <img alt="color swatch" src="data:image/png;base64,'
    + encoded
    + '" style="width:96px"> after</p>'
)
save(document, "10_data_images.docx")
```
