"""22 markdown example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install ".[markdown]"
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
