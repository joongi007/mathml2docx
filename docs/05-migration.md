# Migrating to 1.0.0

Version 1.0.0 converts MathML directly into Word's OMML without an XSL file.

```python
from mathml2docx import convert, MathmlToDocx, TableStyle, ParagraphStyle

convert('<h1>Report</h1><p>Content</p>', 'report.docx',
        table_style=TableStyle.GRID, paragraph_style=ParagraphStyle.NORMAL)

parser = MathmlToDocx()
parser.parse_mathml('<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>').save('fraction.docx')
# python -m pip install 'mathml2docx[latex]'
parser.parse_latex(r'\frac{1}{2} + x^2').save('equation.docx')
```

## Behavior changes

- The core library supports Python 3.6+. Development/documentation tools use uv and Python 3.10+.
- `parse_html_file(input, output)` no longer duplicates `.docx`. Omitted output names
  replace the input extension. The method returns the saved path.
- HTML always uses a BeautifulSoup tree. `fix_html` remains for call compatibility;
  setting it to `False` does not disable tree parsing.
- `get_origin()` returns the same converter instance. Options have one source of
  truth and support both `parser.options.images` and `parser.options['images']`.
- `copy_settings_from()` independently copies all options and style mappings.
- Style helpers require explicit targets: `add_styles_to_run(css, run=run)` and
  `add_styles_to_paragraph(css, paragraph=paragraph)`.
- URL images are not downloaded automatically. Data URLs work by default; local
  files must stay below `img_src_base_path`. Supply `image_loader(source)` returning
  bytes or a file object for URLs or application-specific assets.
- The Office XSL has been removed from the current package. Historical Git
  revisions and releases still require a separate licensing assessment.
- Unsupported MathML raises `UnsupportedMathMLError`. This is not complete support
  for every MathML construct or every LaTeX package.

## Supported mathematics

Tokens (`mi`, `mn`, `mo`, `mtext`, `ms`), grouping, fractions, scripts, square and
indexed roots, delimiters, limits, accents, rectangular matrices, and phantom are
supported. `semantics` converts its first expression and omits annotations.
Selected `menclose` notations and one pair each of pre/post scripts in `mmultiscripts` are supported. Content MathML needs preprocessing or fallback. Not every font,
spacing, accent, or other presentation attribute is reproduced.

LaTeX passes through latex2mathml and the same native converter. Independent answer
checks exposed command, text, accent, and spacing errors in latex2mathml 2.16.
The optional frontend therefore requires Python 3.6.2+ and latex2mathml 3.64+.
HTML/MathML still supports Python 3.6.0/3.6.1; LaTeX requests on those versions
report the required version. HTML dollar delimiters are not interpreted automatically.

Additional checks cover `mathvariant`, string quotes, barless binomial coefficients,
bevelled fractions, explicit fences, over/underlines, accents, and limit function
arguments. Dimensioned `mpadded`, forced equation line breaks, arbitrary negative
spacing, and custom fraction bar thickness raise errors. Some matrix alignment,
CSS, and operator properties are not applied. Supported `mspace` widths use Unicode
space approximations. See [validation and limitations](11-validation.md).

## Styles and templates

Inline CSS supports colors, backgrounds, fonts, sizes, emphasis, underline, strike,
alignment, margins, indentation, and page breaks. RGBA is composited over the
inherited background; zero alpha is transparent. Static `<style>` selectors and
explicitly loaded external CSS are supported.

Install the `markdown` extra to use `parse_markdown()` with tables, fenced code,
and `~~text~~` strikethrough, or provide HTML from another Markdown parser.
Font size alone is not interpreted as heading semantics.

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(style_map={'p': {'quotation': 'Quote'}})
document = Document('template.docx')
parser.add_html_to_document('<p class="quotation">A quotation</p>', document)
# Replace a unique marker, including one split across multiple runs.
parser.replace_html(document, '{{content}}', '<p>Inserted content</p>')
# Inline markers and existing bookmarks are also supported.
# parser.replace_bookmark(document, 'result', '<b>Result</b>')
document.save('output.docx')
```

The document's styles and numbering definitions are retained. New lists receive
new numbering definitions so they restart independently; nested lists use their
corresponding levels. `DocxTemplate` integration uses its underlying `get_docx()` document.

## CLI

```sh
mathml2docx input.html output.docx
python -m mathml2docx input.tex equation.docx --format latex
```

Existing output is refused unless `--force` is supplied.

## Math layout and recovery

MathML without `display` is now inline, matching the standard. To preserve old
block placement, use `MathmlToDocx(default_math_display='block')`. Explicit
`display="block"` and supported CSS display values are honored. Unsupported
formulas still raise by default; `unsupported_math='text'`, `mathml_fallback`
and `mathml_preprocessor` provide explicit recovery. See [equation handling](03-mathematics.md).

## Mathematical correctness and input recovery

MathML defaults now apply consistently from `math` and `mstyle`. Compact-style
movable limits use side scripts, including inside fractions and scripts; formulas
that depended on the former stacked layout may look different. Use explicit
`display="block"` or appropriate `displaystyle` where intended.

Structured accents, merged/ragged mathematical tables and RTL layouts use explicit
recovery when no faithful native representation is available. A forced break on
`mo` is handled the same way as on `mspace`. Malformed argument counts are detected
before recovery, including when an unsupported sibling appears first.

Encoded Unicode mathematical alphabets now carry matching native OMML variants,
including double-struck and bold characters emitted by LaTeX backends. Word can
otherwise decode those characters while losing their intended style.

Token whitespace and string escaping follow MathML rules. XML encoding declarations
do not alter decoded Unicode input. CSS equation styling and XML-aware template
boundaries preserve the selected text, math and surrounding content.
