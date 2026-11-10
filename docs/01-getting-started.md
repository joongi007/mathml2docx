# Getting started

## Installation

The core library supports Python 3.6+. Development and documentation use uv and a
recent Python. Optional LaTeX conversion requires Python 3.6.2+.

These examples describe the repository's 1.0.0 code. Until that version is
published on PyPI, install it from the repository:

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .
# Optional LaTeX frontend:
python -m pip install '.[latex]'
```

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

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_html_file('input.html', 'output.docx')
parser.parse_latex(r'\frac{1}{2}').save('latex.docx')
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
