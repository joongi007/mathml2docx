# List numbering and nesting

Use start values, li values, independent restarts, and nested numbered/bulleted lists.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.09_lists
```

[Generated DOCX](../downloads/examples/09_lists.docx)

[Reference PDF](../assets/previews/09_lists.pdf)

## Complete source

```python
"""09 lists example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1>Lists</h1><ol start="3"><li>Third<ol><li>Nested first</li><li>Nested second</li></ol></li><li value="8">Eighth</li></ol><ol><li>Restart at one</li></ol><ul><li>Bullet<ul><li>Nested bullet</li></ul></li></ul>'
)
save(document, "09_lists.docx")
```
