# Quick start

Save HTML with one convert() call and receive a Document.

## Run

```sh
python -m examples.01_quickstart
```

[Generated DOCX](../downloads/examples/01_quickstart.docx)

[Reference PDF](../assets/previews/01_quickstart.pdf)

## Complete source

```python
"""01 quickstart example."""

from mathml2docx import convert

from .support import OUTPUT

document = convert(
    "<h1>Hello</h1><p>HTML to editable Word.</p>", OUTPUT / "01_quickstart.docx"
)
print(OUTPUT / "01_quickstart.docx")
```
