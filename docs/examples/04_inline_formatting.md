# Inline formatting and colors

Apply emphasis, underline, strike, scripts, code, and alpha-composited colors.

## Run

```sh
python -m examples.04_inline_formatting
```

[Generated DOCX](../downloads/examples/04_inline_formatting.docx)

[Reference PDF](../assets/previews/04_inline_formatting.pdf)

## Complete source

```python
"""04 inline formatting example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Inline formatting</h1><p><b>Bold</b> <i>italic</i> <u>underline</u>
<del>removed</del> H<sub>2</sub>O x<sup>2</sup> <code>code()</code></p>
<p style="font-family:DejaVu Sans;font-size:14pt;color:navy">Named color and font</p>
<p style="background-color:blue"><span style="background-color:rgba(255,0,0,.5)">Purple blend</span></p>
<pre>first\tsecond\n  indented code</pre>""")
save(document, "04_inline_formatting.docx")
```
