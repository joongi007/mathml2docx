# Links and anchors

Use external/internal links, id/name anchors, and links without href.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.20_links
```

[Generated DOCX](../downloads/examples/20_links.docx)

[Reference PDF](../assets/previews/20_links.pdf)

## Complete source

```python
"""20 links example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1 id="intro">Introduction</h1><p><a href="https://example.com">External link</a> <a href="#intro">Back to introduction</a> <a name="legacy">Named anchor</a> <a>Link without href</a></p>'
)
save(document, "20_links.docx")
```
