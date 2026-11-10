# Inline base64 images

Place data URL images inside a paragraph and set their display width.

## Run

```sh
python -m examples.10_data_images
```

[Generated DOCX](../downloads/examples/10_data_images.docx)

[Reference PDF](../assets/previews/10_data_images.pdf)

## Complete source

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
