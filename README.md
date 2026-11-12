# mathml2docx

[English](README.md) · [한국어](README.ko.md) · [Documentation](https://joongi007.github.io/mathml2docx/)

Convert HTML and MathML into Word documents with Python. Create reports, worksheets
and templates with **editable equations**, formatted text, tables and images.
Microsoft Office is not required to generate a document.

Python 3.6+ · Optional LaTeX and Markdown inputs · MIT license

## Installation

This README describes the 1.0 API. Install the repository version while 1.0 is
unreleased on PyPI:

```sh
python -m pip install 'git+https://github.com/joongi007/mathml2docx.git@master'
# With optional LaTeX and Markdown support:
python -m pip install 'mathml2docx[latex,markdown] @ git+https://github.com/joongi007/mathml2docx.git@master'
```

Python 3.6.2+ is required for the optional LaTeX frontend. Library users do not need uv.
For a reproducible installation, replace `master` with a reviewed commit or release tag.

## Your first Word document

```python
from mathml2docx import convert

convert('''
<h1>Lesson notes</h1>
<p>The value <math><mfrac><mn>1</mn><mn>2</mn></mfrac></math> is one half.</p>
<math display="block"><msup><mi>x</mi><mn>2</mn></msup></math>
''', 'lesson.docx')
```

Open `lesson.docx` in Word to edit its text and equations. `convert()` also returns
a python-docx `Document`; omit the output path to continue editing it in Python.

## What it supports

| Input or task | Features |
| --- | --- |
| HTML | Headings, paragraphs, links, nested lists and text formatting |
| Tables | Merged cells, nested tables and Word table styles |
| Images | Data URLs, configured local files and explicit application loaders |
| CSS | Supported selectors, fonts, colors, alignment and page breaks |
| MathML | Fractions, roots, scripts, limits, accents, matrices, selected enclosures and isotope scripts |
| LaTeX / Markdown | Optional frontends using latex2mathml and Python-Markdown |
| Templates | Add to an existing document or cell; replace markers and bookmarks |

The converter implements a documented subset of HTML, CSS and Presentation MathML.
It does not reproduce a complete browser layout.

## Equation layout and unsupported input

`<math>` is **inline by default**, following MathML. Use `display="block"` for a
separate display equation. To retain block behavior for input that omits `display`:

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(default_math_display='block')
```

Unsupported mathematical structures raise `UnsupportedMathMLError` by default.
Applications handling mixed input can select `unsupported_math='text'` to preserve
the formula's XML visibly, provide `mathml_fallback(source, error)` returning text
or an image, or normalize input with `mathml_preprocessor(source)`. Recovery emits
`MathMLFallbackWarning`; invalid XML still raises an error.
See [equation handling](https://joongi007.github.io/mathml2docx/03-mathematics/)
for supported notations and complete examples.

## LaTeX, Markdown and command line

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_latex(r'\frac{1}{2} + x_1^2').save('equation.docx')
parser.parse_markdown('# Notes\n\n**Bold** and ~~removed~~ text.').save('notes.docx')
```

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx input.html output.docx --default-math-display block --unsupported-math text
```

Use `--force` to replace an existing output file. HTML dollar delimiters are not
interpreted as LaTeX. Network images and stylesheets require explicit loaders.

## Guides and examples

- [Getting started](https://joongi007.github.io/mathml2docx/01-getting-started/) · [API and options](https://joongi007.github.io/mathml2docx/02-api/) · [Recipes](https://joongi007.github.io/mathml2docx/08-recipes/)
- [Runnable examples and DOCX downloads](https://joongi007.github.io/mathml2docx/examples/00-index/): formatting, templates, scientific reports, chemistry and fallback rendering.
- [MathML fidelity example](https://joongi007.github.io/mathml2docx/examples/30-mathml-fidelity/): inherited defaults, accents, equation styles, links and template replacement.
- [Migration from 0.x](https://joongi007.github.io/mathml2docx/05-migration/) · [Compatibility and validation](https://joongi007.github.io/mathml2docx/11-validation/)
- [한국어 문서](https://joongi007.github.io/mathml2docx/ko/)

For headless PDF conversion with LibreOffice, install **Writer and Math**, plus
appropriate fonts. Writer-only installations can leave equations blank. The
[rendering guide](https://joongi007.github.io/mathml2docx/11-validation/#libreoffice)
includes installation and verification commands. Use `math_target='libreoffice'`
with an explicit fallback for known enclosure differences.

## Contributing and license

Work from `develop`; see [development and releases](https://joongi007.github.io/mathml2docx/09-development-release/)
for setup, tests and publishing. Changes are listed in [CHANGELOG.md](CHANGELOG.md).

[MIT](LICENSE), derived from [html2docx](https://github.com/pqzx/html2docx).
Dependencies retain their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
The 1.0 converter constructs OMML directly and includes no Office XSL. Historical
0.x distributions are covered separately in the [provenance record](https://joongi007.github.io/mathml2docx/06-xsl-provenance/).
