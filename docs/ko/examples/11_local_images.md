# 로컬 이미지

명시한 기준 경로 아래의 이미지를 읽습니다. 기준 밖 경로는 허용하지 않습니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.11_local_images
```

[생성된 DOCX](../downloads/examples/11_local_images.docx)

[참조 PDF](../assets/previews/11_local_images.pdf)

## 전체 코드

```python
"""11 local images example."""

from mathml2docx import MathmlToDocx

from .support import ROOT, save

parser = MathmlToDocx(img_src_base_path=ROOT / "assets")
document = parser.parse_html_string(
    '<h1>Local assets</h1><p><img src="swatch.png" width="120"></p>'
)
save(document, "11_local_images.docx")
```
