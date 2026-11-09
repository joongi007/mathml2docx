# mathml2docx
The fork in [htmldocx](https://github.com/pqzx/html2docx) converts html (including mathml) to docx     
Dependencies: Python 3.6+, python-docx, BeautifulSoup, lxml, tinycss2 and Pillow.

The repository now targets **1.0.0** (not yet published to PyPI). MathML is converted
directly to editable OMML without an Office XSL file. Install from this checkout
with `pip install .`, or `pip install ".[latex]"` for LaTeX support.

```python
from mathml2docx import convert, MathmlToDocx, TableStyle

convert("<p>Hello</p>", "output.docx", table_style=TableStyle.GRID)
MathmlToDocx().parse_latex(r"\frac{1}{2}").save("equation.docx")
```

See [1.0 migration](docs/05-migration.md), [upstream issue audit](docs/07-upstream-audit.md),
and [XSL provenance](docs/06-xsl-provenance.md). URL images no longer trigger implicit
network requests; use an explicit loader if needed.

### Documentation and agent skill

Documentation source: [docs/index.md](docs/index.md).
The GitHub Pages deployment target is [joongi007.github.io/mathml2docx](https://joongi007.github.io/mathml2docx/).
See [publishing instructions](docs/04-publishing.md) to enable Pages and build locally.

An installable [conversion skill](skills/mathml2docx/SKILL.md), a downloadable skill ZIP,
and `llms.txt` / `llms-full.txt` are provided with the documentation build.
See [AI integration](docs/03-agents.md). These static resources do not run an MCP server.

### To install

`pip install mathml2docx`

### Imporvements
- Add: Convert mathml to docx formula
- Add: MathmlToDocx, a wrapper class for InteliSense and encapsulation
- Add: Etc...
- Fix: Known errors in the original repository

### Usage

Add strings of html to an existing docx.Document object

```
from docx import Document
from mathml2docx import MathmlToDocx

document = Document()
new_parser = MathmlToDocx()
# do stuff to document

html = '<h1>Hello world</h1>'
new_parser.add_html_to_document(html, document)

# do more stuff to document
document.save('your_file_name')
```

Convert files directly

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.parse_html_file(input_html_file_path, output_docx_file_path)
```

Convert files from a string

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
docx = new_parser.parse_html_string(input_html_file_string)
```

Change table styles

Tables are not styled by default. Use the `table_style` attribute on the parser to set a table
style. The style is used for all tables.

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.table_style = 'Light Shading Accent 4'
```

To add borders to tables, use the `TableGrid` style:

```
new_parser.table_style = 'Table Grid'
```

Default table styles can be found
here: https://python-docx.readthedocs.io/en/latest/user/styles-understanding.html#table-styles-in-default-template

Change default paragraph style

No style is applied to the paragraphs by default. Use the `paragraph_style` attribute on the parser
to set a default paragraph style. The style is used for all paragraphs. If additional styling (
color, background color, alignment...) is defined in the HTML, it will be applied after the
paragraph style.

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.paragraph_style = 'Quote'
```

Default paragraph styles can be found
here: https://python-docx.readthedocs.io/en/latest/user/styles-understanding.html#paragraph-styles-in-default-template

### Runnable examples

[22 runnable examples](docs/examples/00-index.md) cover CSS stylesheets, tables, lists, images,
MathML/LaTeX, Word styles, markers, bookmarks, docxtpl and mixed reports.
Each documentation page includes full source, a generated DOCX and a reference PDF.

```sh
uv sync --locked --extra latex --extra markdown --group examples
uv run --no-sync python -m examples.run_all
```

See [task recipes](docs/08-recipes.md) for the complete feature map and low-level API examples.

Development uses modern Python and uv; installed libraries support Python 3.6+.
See [development and release instructions](docs/09-development-release.md) for
legacy compatibility tests, local preservation tags, and approval-gated PyPI publishing.
