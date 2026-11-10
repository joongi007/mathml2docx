# 자산 로더와 이미지 직접 삽입

논리 자산 ID를 bytes로 해석하고 BytesIO 이미지를 셀에 직접 추가합니다.

## 실행

```sh
python -m examples.12_asset_loader
```

[생성된 DOCX](../downloads/examples/12_asset_loader.docx)

[참조 PDF](../assets/previews/12_asset_loader.pdf)

## 전체 코드

```python
"""12 asset loader example."""

from io import BytesIO

from mathml2docx import MathmlToDocx

from .support import ROOT, save

# Resolve allowed logical asset IDs. No network access or arbitrary file paths.
assets = {"asset:logo": (ROOT / "assets/swatch.png").read_bytes()}
parser = MathmlToDocx(image_loader=assets.__getitem__)
document = parser.parse_html_string(
    '<p>Asset <img src="asset:logo" width="80"> inline</p>'
)
cell = document.add_table(1, 1).cell(0, 0)
parser.add_image_to_cell(cell, BytesIO(assets["asset:logo"]))
save(document, "12_asset_loader.docx")
```
