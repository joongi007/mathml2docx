# mathml2docx

[English](https://github.com/joongi007/mathml2docx/blob/master/README.md) · [한국어](https://github.com/joongi007/mathml2docx/blob/master/README.ko.md)

Turn HTML and MathML into Word documents with Python. Equations stay editable in
Word, so you can use the output in reports, worksheets, and document templates.
Microsoft Office does not need to be installed to generate a document.

**Python 3.6+** · Optional LaTeX and Markdown support · MIT license

## Install

The examples below use the **1.0 code in this repository**. Install the checkout
to follow along; the older PyPI release has a different API.

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .
```

For LaTeX and Markdown, install the optional dependencies:

```sh
python -m pip install '.[latex,markdown]'
```

LaTeX requires Python **3.6.2+**. You do not need uv to use the library.

## Create your first document

```python
from mathml2docx import convert

html = '''
<h1>Lesson notes</h1>
<p>This fraction remains editable in Word:</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>
'''

convert(html, 'lesson.docx')
```

Run the code and open `lesson.docx`. To keep editing in Python, omit the output
path with `document = convert(html)`, then call `document.save('lesson.docx')`
when you are ready.

## What can I convert?

- **HTML:** headings, paragraphs, links, text formatting, and lists.
- **Tables:** merged cells, nested tables, and Word table styles.
- **Images:** embedded data URLs, explicitly configured local files, and custom loaders.
- **Styles:** supported CSS selectors, fonts, colors, alignment, and page breaks.
- **Equations:** supported MathML fractions, roots, scripts, limits, accents, and matrices.
- **Existing documents:** add content to a document or cell, or replace a marker/bookmark.

This library supports a subset of HTML/CSS and MathML. It does not reproduce a
whole browser page. Unsupported MathML elements raise `UnsupportedMathMLError`.
See [support and migration](https://github.com/joongi007/mathml2docx/blob/master/docs/05-migration.md)
and [validation and known limitations](https://github.com/joongi007/mathml2docx/blob/master/docs/11-validation.md)
for details, including the remaining direct Word checks.

## More ways to use it

| I want to… | Example |
| --- | --- |
| Convert HTML files and handle Unicode | [Files and encoding](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/02_files_unicode.md) |
| Add HTML to an existing document or table cell | [Existing documents](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/03_existing_document.md) |
| Apply Word styles and map HTML classes | [Word styles](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/06_word_styles.md) |
| Replace content in a template | [Markers](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/15_markers.md) · [Bookmarks](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/16_bookmarks.md) |
| Review advanced scientific formulas and templates | [Research report](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/25_research_report.md) · [Workbook](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/26_template_workbook.md) · [Advanced LaTeX](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/27_advanced_latex.md) |
| Combine equations, tables, and images | [Complex equations](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/23_complex_equations.md) · [Mixed report](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/24_dense_report.md) |

## LaTeX and Markdown

After installing the optional dependencies above:

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_latex(r'\frac{1}{2} + x_1^2').save('equation.docx')
parser.parse_markdown('# Notes\n\n**Bold** and ~~removed~~ text.').save('notes.docx')
```

LaTeX is an explicit input format. Dollar-delimited expressions in HTML are not
converted automatically.

## Command line

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx notes.md notes.docx --format markdown
```

Use `--force` to replace an existing output file. Images from URLs and external
stylesheets are not downloaded automatically; Python applications can supply
explicit loaders.

## Documentation

- [Getting started](https://github.com/joongi007/mathml2docx/blob/master/docs/01-getting-started.md) · [API reference](https://github.com/joongi007/mathml2docx/blob/master/docs/02-api.md) · [Recipes](https://github.com/joongi007/mathml2docx/blob/master/docs/08-recipes.md)
- [All 27 runnable examples](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/00-index.md), with complete source and commands to generate DOCX locally.
- Web documentation: [English](https://joongi007.github.io/mathml2docx/) · [한국어](https://joongi007.github.io/mathml2docx/ko/). The site becomes available after Pages activation and a successful deployment; deployed builds include example downloads.

## Contributing

Start changes on `develop`. See the [development and release guide](https://github.com/joongi007/mathml2docx/blob/master/docs/09-development-release.md)
for uv setup, tests, branching, and publishing. See the [changelog](https://github.com/joongi007/mathml2docx/blob/master/CHANGELOG.md)
for the 1.0 changes.

## License

[MIT](https://github.com/joongi007/mathml2docx/blob/master/LICENSE), with attribution to the original
[html2docx](https://github.com/pqzx/html2docx) project. Dependencies retain their own licenses;
see [third-party notices](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md).
The 1.0 converter builds Word equations directly without the former Office XSL.
Historical XSL copies have a separate, unresolved [licensing scope](https://github.com/joongi007/mathml2docx/blob/master/docs/10-licensing.md).
