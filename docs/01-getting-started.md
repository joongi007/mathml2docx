# Getting started

## Installation

The core library supports Python 3.6+. Install the published package from PyPI
in your project's Python environment:

```sh
python -m pip install mathml2docx
```

HTML and MathML work with the core package. Install the extras for LaTeX or
Markdown input:

```sh
python -m pip install "mathml2docx[latex]"
python -m pip install "mathml2docx[markdown]"
# Both optional frontends:
python -m pip install "mathml2docx[latex,markdown]"
```

Optional LaTeX conversion requires Python 3.6.2+. Check the installed version with:

```sh
python -m pip show mathml2docx
```

To update an existing installation, use `python -m pip install --upgrade mathml2docx`.
See [migration](05-migration.md) when upgrading from 0.x, and include your extras
in the upgrade command if needed.

For a project already using uv, `uv add mathml2docx` adds the published dependency;
use `uv add "mathml2docx[latex,markdown]"` for both extras. Library installation
does not require Git or a repository checkout. Source and contributor setup is in
[development and releases](09-development-release.md).

### Python 3.6

Use a pip version that supports Python 3.6 and its compatible dependency wheels:

```sh
python -m pip install --upgrade "pip>=21.3,<22"
python -m pip install mathml2docx
```

pip selects dependency versions compatible with the interpreter. The optional
LaTeX frontend still requires Python 3.6.2+.

## Convert HTML and equations

```python
from mathml2docx import convert

html = '''<h1>Equation example</h1>
<p>The following is a fraction.</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>'''
convert(html, 'example.docx')
```

`convert()` returns a python-docx `Document`. Omit the output path to return the
document without saving it. Neither XSL nor Microsoft Office is required.

To convert an existing HTML file named `input.html`:

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_html_file('input.html', 'output.docx')
```

After installing the `latex` extra:

```python
from mathml2docx import MathmlToDocx

MathmlToDocx().parse_latex(r'\frac{1}{2}').save('latex.docx')
```

## Add to an existing document

```python
from docx import Document
from mathml2docx import MathmlToDocx

document = Document()
document.add_paragraph('Existing content')
MathmlToDocx().add_html_to_document('<p>Additional content</p>', document)
document.save('combined.docx')
```

Use `add_html_to_cell(html, cell)` for a table cell.
Existing users should read [the 1.0.0 migration guide](05-migration.md).
