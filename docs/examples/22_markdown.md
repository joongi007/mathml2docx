# Markdown integration

Convert headings, tables, lists, code, and strikethrough with the optional frontend.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.22_markdown
```

[Generated DOCX](../downloads/examples/22_markdown.docx)

[Reference PDF](../assets/previews/22_markdown.pdf)

## Complete source

```python
"""22 markdown example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install "mathml2docx[markdown]"
source = """# Markdown example

1. First
2. Second

| A | B |
|---|---|
| 1 | 2 |

~~Deleted content~~

```python
print('hello')
```
"""
document = MathmlToDocx().parse_markdown(source)
save(document, "22_markdown.docx")
```
