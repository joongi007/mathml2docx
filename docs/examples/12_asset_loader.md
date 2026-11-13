# Asset loaders and direct images

Resolve logical asset IDs to bytes and insert BytesIO images into cells.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.12_asset_loader
```

[Generated DOCX](../downloads/examples/12_asset_loader.docx)

[Reference PDF](../assets/previews/12_asset_loader.pdf)

## Complete source

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
