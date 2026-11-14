# Getting started

## Installation

The core library supports Python 3.6+; optional LaTeX requires 3.6.2+.
Choose one of the following methods to install the published PyPI package.
HTML and MathML work with the core package; extras add LaTeX and Markdown input.
Git and a repository checkout are not required.

### pip

Install in your project's Python environment. If needed, create one with
`python -m venv .venv` and [activate it](https://docs.python.org/3/library/venv.html#how-venvs-work)
using the command for your operating system.

```sh
python -m pip install mathml2docx
```

For optional inputs, choose the extras you need:

```sh
python -m pip install "mathml2docx[latex]"
python -m pip install "mathml2docx[markdown]"
# Both optional frontends:
python -m pip install "mathml2docx[latex,markdown]"
```

Check the installed version with:

```sh
python -m pip show mathml2docx
```

Update with `python -m pip install --upgrade mathml2docx`, or
`python -m pip install --upgrade "mathml2docx[latex,markdown]"` if using both extras.
Run your saved Python script with `python report.py`.

### uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) separately.
For a new project, run `uv init --bare report-project`, then `cd report-project`.
In an existing uv project, use its directory directly.

```sh
uv add mathml2docx
# Or include both optional inputs:
uv add "mathml2docx[latex,markdown]"
uv run python -c "import mathml2docx; print(mathml2docx.__version__)"
```

For a single extra, use `uv add "mathml2docx[latex]"` or
`uv add "mathml2docx[markdown]"`. uv manages the environment and records dependencies
in `pyproject.toml` and `uv.lock`. Run your saved script with `uv run python report.py`.

Update within your declared version constraints:

```sh
uv lock --upgrade-package mathml2docx
uv sync
```

### Poetry

Install [Poetry](https://python-poetry.org/docs/#installation) separately;
the current Poetry tool requires Python 3.10+. In a new project directory,
run `poetry init` and set the Python range to match the interpreters you support.
In an existing Poetry project, use its directory directly.

```sh
poetry add mathml2docx
# Or include both optional inputs:
poetry add "mathml2docx[latex,markdown]"
poetry run python -c "import mathml2docx; print(mathml2docx.__version__)"
```

For a single extra, use `poetry add "mathml2docx[latex]"` or
`poetry add "mathml2docx[markdown]"`. Poetry records dependencies in `pyproject.toml`
and `poetry.lock`. Run your saved script with `poetry run python report.py`.
Update within your declared version constraints with `poetry update mathml2docx`.

### Version compatibility

Package managers have their own Python requirements; the library's Python 3.6
support does not require installing a modern tool on Python 3.6. Keep your project's
requirements or lockfile for repeatable installs. See [migration](05-migration.md)
when upgrading from 0.x. Source and contributor setup is in
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
If upgrading from 0.x, read [the migration guide](05-migration.md).
