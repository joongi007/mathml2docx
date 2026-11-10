# mathml2docx

[English](https://github.com/joongi007/mathml2docx/blob/master/README.md) · [한국어](https://github.com/joongi007/mathml2docx/blob/master/README.ko.md)

Convert HTML and MathML into **editable Word documents (`.docx`)** from Python.
Optional frontends also accept LaTeX and Markdown.

The core library supports **Python 3.6+**. It builds OMML equations directly;
Microsoft Office and `MML2OMML.XSL` are not required. Optional LaTeX conversion
requires **Python 3.6.2+** and latex2mathml 3.64+.

This repository contains **1.0.0 release preparation code**. Until 1.0.0 is
published, install from the repository to use the APIs below.
`pip install mathml2docx` installs the version currently published on PyPI.

## Installation

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .

# Install only the optional features you need.
python -m pip install '.[latex]'
python -m pip install '.[markdown]'
python -m pip install '.[latex,markdown]'
```

Library users do not need uv. The installer selects dependencies compatible with
the running Python version. Development and documentation use uv and a recent Python.

## Quick start

```python
from mathml2docx import convert, TableStyle

html = '''<h1>Analysis report</h1>
<p>The following equation remains editable.</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>
<table><tr><th>Item</th><th>Result</th></tr>
<tr><td>Sample count</td><td>24</td></tr></table>'''

document = convert(html, 'report.docx', table_style=TableStyle.GRID)
```

`convert()` returns a python-docx `Document`. Omit the output path to make further
changes before calling `document.save('report.docx')`.

## Files, existing documents, and table cells

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
output = parser.parse_html_file('input.html', 'output.docx', encoding='utf-8')

document = Document('template.docx')
parser.add_html_to_document('<h2>New section</h2><p>Additional content.</p>', document)
cell = document.add_table(rows=1, cols=1).cell(0, 0)
parser.add_html_to_cell('<b>Content inside a cell</b>', cell)
document.save('combined.docx')
```

`parse_html_file()` returns the saved `Path`, adds `.docx` only once, and defaults
to replacing the input extension when no output name is supplied.

## LaTeX and Markdown

```python
parser.parse_latex(r'\frac{1}{2} + x_1^2').save('equation.docx')
parser.parse_markdown('# Heading\n\n~~Removed~~ and **bold** text.').save('notes.docx')
```

Install the `latex` or `markdown` extra respectively. Markdown supports tables,
fenced code, and strikethrough. Dollar delimiters inside HTML are not interpreted
as LaTeX automatically.

## Styles and templates

Use `TableStyle` and `ParagraphStyle` constants, or names defined in your Word
template. Map HTML classes to Word styles and replace existing content:

```python
from mathml2docx import MathmlToDocx, ParagraphStyle

parser = MathmlToDocx(
    paragraph_style=ParagraphStyle.NORMAL,
    style_map={'p': {'quotation': 'Quote'}},
    stylesheet='.notice { color: navy; font-weight: bold }',
)
parser.add_html_to_document('<p class="quotation">A quotation.</p>', document)
parser.replace_html(document, '{{content}}', '<p class="notice">Updated content.</p>')
# For an existing named bookmark:
# parser.replace_bookmark(document, 'result', '<b>Updated result</b>')
```

Markers may span multiple runs. Replacement also supports table cells, block
content, and bookmark ranges. External CSS requires an explicit stylesheet loader.

## Supported features and limits

| Area | Supported features |
| --- | --- |
| Text | Headings, paragraphs, bold, italic, underline, strike, scripts, code |
| Lists | Numbered and bulleted lists, nesting, start values, independent restarts |
| Tables | `thead`/`tbody`, row/column spans, nested tables, Word table styles |
| Images | Data URLs, files below an explicit base directory, custom asset loaders, inline sizing |
| CSS | Static selectors, inheritance, cascade, fonts, colors, margins, alignment, page breaks |
| MathML | Tokens, groups, fractions, scripts, radicals, delimiters, limits, accents, matrices, phantom |
| Templates | Existing Document/cells, docxtpl integration, marker and bookmark replacement |
| Optional | LaTeX, Markdown, CLI, an agent conversion skill |

This is not a browser renderer or a complete MathML/LaTeX implementation.
Unsupported elements such as `menclose`, `mmultiscripts`, and Content MathML
raise `UnsupportedMathMLError`. Some presentation attributes are approximated or
not applied. See [migration and support scope](https://github.com/joongi007/mathml2docx/blob/master/docs/05-migration.md)
and [validation and limitations](https://github.com/joongi007/mathml2docx/blob/master/docs/11-validation.md).

URL images are never downloaded implicitly. Local images must stay below
`img_src_base_path`; other assets require an `image_loader` callback. Applications
define resource limits and access rules for their own inputs and loaders.

## CLI

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx article.md article.docx --format markdown
python -m mathml2docx input.html output.docx --encoding utf-8
```

Existing output files are refused unless `--force` is supplied.

## Documentation and examples

- [Getting started](https://github.com/joongi007/mathml2docx/blob/master/docs/01-getting-started.md) · [API and options](https://github.com/joongi007/mathml2docx/blob/master/docs/02-api.md)
- [Changelog](https://github.com/joongi007/mathml2docx/blob/master/CHANGELOG.md)
- [24 runnable examples](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/00-index.md) · [Recipes](https://github.com/joongi007/mathml2docx/blob/master/docs/08-recipes.md)
- [Complex equation gallery](https://github.com/joongi007/mathml2docx/blob/master/examples/23_complex_equations.py) · [Mixed report](https://github.com/joongi007/mathml2docx/blob/master/examples/24_dense_report.py)
- [Validation and limitations](https://github.com/joongi007/mathml2docx/blob/master/docs/11-validation.md) · [Text inputs and independent answers](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/README.md)
- [Review of 49 upstream issues](https://github.com/joongi007/mathml2docx/blob/master/docs/07-upstream-audit.md) · [Choosing a tool](https://github.com/joongi007/mathml2docx/blob/master/docs/12-choosing.md)
- [Agent skill and machine-readable documentation](https://github.com/joongi007/mathml2docx/blob/master/docs/03-agents.md)
- [Documentation deployment](https://github.com/joongi007/mathml2docx/blob/master/docs/04-publishing.md) · [Development and publishing](https://github.com/joongi007/mathml2docx/blob/master/docs/09-development-release.md)

The documentation site is configured for <https://joongi007.github.io/mathml2docx/>.
English is the default; [한국어 documentation](https://joongi007.github.io/mathml2docx/ko/)
covers the same guides and examples. The language selector keeps the current page.
It becomes available after GitHub Pages is enabled and deployment succeeds.
Generated DOCX files are not committed; run examples locally or use downloads
from a deployed documentation build.

## Development and verification

Use uv 0.13.7+ and the development Python pinned in `.python-version`.
This does not change the library's minimum Python version.

```sh
uv sync --locked --extra latex --extra markdown --extra test --group docs --group examples
uv run --no-sync python -m pytest -q
uv run --no-sync python -m unittest tests.test_docx_oracles -v
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/build_docs.py
uv build
uv run --no-sync python scripts/check_dist.py
uv run --no-sync twine check dist/*

# Requires Docker: source and wheel installation on real Python 3.6.
bash scripts/test_legacy.sh
```

CI covers each Python minor from 3.6 through 3.14, plus Windows and macOS conversion
checks. PyPI publishing requires an explicitly published stable GitHub Release and
passing checks. Configure a Trusted Publisher and reviewers for the `pypi`
environment before publishing. Ordinary pushes do not upload to PyPI.
Candidate GitHub Releases publish to TestPyPI through a separately configured
`testpypi` environment. Manual workflow runs only validate and build.

## License and provenance

Project code is [MIT-licensed](https://github.com/joongi007/mathml2docx/blob/master/LICENSE),
retaining the original [html2docx](https://github.com/pqzx/html2docx) attribution.
Dependencies retain their own licenses; see [third-party notices](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md).

The 1.0.0 distribution excludes Office's `MML2OMML.XSL` and code that loads it.
The native converter builds OMML nodes without copying the old XSL templates.
This does not resolve redistribution rights for historical Git revisions,
preservation tags, or old packages. See [the provenance investigation](https://github.com/joongi007/mathml2docx/blob/master/docs/06-xsl-provenance.md)
and [licensing scope](https://github.com/joongi007/mathml2docx/blob/master/docs/10-licensing.md).
