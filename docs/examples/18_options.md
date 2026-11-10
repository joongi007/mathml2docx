# Options and settings copies

Disable images, tables, math, or styles and independently copy settings.

## Run

```sh
python -m examples.18_options
```

[Generated DOCX](../downloads/examples/18_options.docx)

[Reference PDF](../assets/previews/18_options.pdf)

## Complete source

```python
"""18 options example."""

from mathml2docx import MathmlToDocx

from .support import save

source = MathmlToDocx(images=False, tables=False, mathml=False)
parser = MathmlToDocx()
parser.copy_settings_from(source)
parser.options.styles = False
assert parser.get_origin() is parser
html = '<h1>Options</h1><p><b>Plain</b><img src="missing"></p><table><tr><td>Skipped</td></tr></table><math><mi>x</mi></math>'
save(parser.parse_html_string(html), "18_options.docx")
```
