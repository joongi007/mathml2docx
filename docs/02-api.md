# API and options

## Public API

```python
from mathml2docx import convert, MathmlToDocx, TableStyle, ParagraphStyle

convert('<p>Content</p>', 'output.docx', paragraph_style=ParagraphStyle.NORMAL)
parser = MathmlToDocx(table_style=TableStyle.GRID)
```

`HtmlToDocx` remains available under its original name. Use `MathmlToDocx` in new code.

| Method | Result |
| --- | --- |
| `convert(html, output=None, **options)` | Return a Document; save it when an output path is supplied |
| `parser.convert(html, output=None)` | Convert using the instance's settings |
| `parse_html_string(html)` | Return a new Document |
| `parse_html_file(input, output=None, encoding='utf-8')` | Return the saved Path; add the extension only once |
| `parse_mathml(source)` | Return a Document containing native OMML equations |
| `parse_markdown(source)` | Use optional Markdown to convert headings, tables, code, and strike |
| `parse_latex(source)` | Return a Document using optional latex2mathml; requires Python 3.6.2+ |
| `add_html_to_document(html, document)` | Add to a Document, table cell, or DocxTemplate |
| `add_html_to_cell(html, cell)` | Add to a table cell |
| `add_image_to_cell(cell, image)` | Add a BytesIO image to a document or cell |
| `copy_settings_from(other)` | Independently copy options and style mappings |
| `replace_html(document, marker, html)` | Replace a unique marker, including across runs, with inline or block HTML |
| `replace_bookmark(document, name, html)` | Replace a bookmark range with HTML |
| `get_origin()` | Return the current converter instance |

## Constructor options

| Argument | Default | Behavior |
| --- | --- | --- |
| `fix_html` | `True` | Compatibility argument; tree parsing always runs |
| `images` | `True` | Enable image handling |
| `tables` | `True` | Enable table handling |
| `mathml` | `True` | Enable MathML handling |
| `styles` | `True` | Enable formatting |
| `img_src_base_path` | `None` | Allow local images only below this directory |
| `image_loader` | `None` | Explicit callback returning bytes or a file object for an asset source |
| `table_style` | `None` | Word table style name or TableStyle constant |
| `paragraph_style` | `None` | Word paragraph style name or ParagraphStyle constant |
| `stylesheet` | `""` | Additional CSS stylesheet text |
| `stylesheet_loader` | `None` | Explicit callback returning CSS text for an external source |
| `style_map` | `None` | Tag → class → Word style name mapping |
| `default_math_display` | `'inline'` | Layout when the MathML display attribute is omitted; `'block'` restores the older behavior |
| `unsupported_math` | `'error'` | `'error'` raises; `'text'` visibly preserves the unsupported formula's XML |
| `mathml_preprocessor` | `None` | Callback accepting and returning a complete MathML string |
| `mathml_fallback` | `None` | Callback `(source, error)` returning literal text, image bytes or `BytesIO` |
| `math_target` | `'word'` | `'libreoffice'` requests explicit upright identifiers and recovery for known lossy native notation |

Change options after construction with, for example, `parser.options.images = False`.
Set styles and mappings through `parser.table_style`, `parser.paragraph_style`, and
`parser.style_map`. Referenced styles must exist in the Word template.

The default image loader handles data URLs and files below an explicitly configured
base directory. It does not download URLs. If an `image_loader` uses the network,
the calling application must enforce its own destination, size, and time limits.

See [migration and support scope](05-migration.md), [complete examples](examples/00-index.md),
and [recipes](08-recipes.md).

[Equation layout, supported enclosures, chemical notation and recovery](03-mathematics.md).
