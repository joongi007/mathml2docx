---
name: mathml2docx
description: Convert HTML containing MathML into Word (.docx) documents with the Python mathml2docx library. Use for HTML file conversion or adding HTML and editable equations to existing Word documents.
---

# HTML and MathML to Word

Use `mathml2docx.MathmlToDocx`. Install the library in the task's Python environment
if it is missing. This skill does not bundle the library.

For file conversion, run the bundled helper:

```sh
python scripts/convert.py input.html output.docx
```

Resolve the script relative to this skill's directory. It accepts UTF-8 HTML,
preserves the exact output path, and refuses to overwrite an existing file.
Use the repository 1.0.0 version; older PyPI versions have different behavior.
Images are disabled in the helper by default. `--images` enables data URL images.
The 1.0 library never downloads URL images implicitly. Local paths require
`img_src_base_path`, and other sources require an explicit `image_loader` callback.

For integration into Python code:

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(images=False)
document = parser.parse_html_string(html)
document.save(output_path)
```

- MathML is parsed directly into OMML without an Office XSL file. Unsupported
  structures raise `UnsupportedMathMLError`; do not replace them with missing text.
- LaTeX math: install the repository with the `latex` extra and call
  `parser.parse_latex(source).save(output_path)`. HTML dollar delimiters are not
  automatically interpreted. Only the supported MathML subset can be converted.
- `parse_html_file(input, output)` in 1.0 preserves `.docx` without doubling it.
  The helper preserves the exact output path and refuses overwrites.
- For an existing python-docx document, use `add_html_to_document(html, document)`;
  for a table cell, use `add_html_to_cell(html, cell)` and save the owning document.
- Use `TableStyle` and `ParagraphStyle` constants or names present in the Word template.
- Check the resulting document and report its path. If rendering cannot be checked
  in Word or a compatible viewer, say so; XML inspection alone cannot prove layout.

API and limitations: https://joongi007.github.io/mathml2docx/02-api/

- Stylesheets: pass `stylesheet` text or an explicit `stylesheet_loader` callback;
  CSS resources are never fetched automatically.
- Replace markers spanning runs with `replace_html(document, marker, html)`;
  replace a named bookmark range with `replace_bookmark(document, name, html)`.
- Full runnable examples and reference outputs:
  https://joongi007.github.io/mathml2docx/examples/00-index/
- Markdown: install the `markdown` extra and use `parse_markdown(source)` for
  tables, fenced code and strikethrough; literal code spans remain untouched.
