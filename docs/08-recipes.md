# Recipes

[The 30 runnable examples](examples/00-index.md) include full source, generated DOCX
downloads and LibreOffice reference PDFs. This page covers
common combinations and lower-level APIs.

## Convert several files

Place the HTML files to convert in an `input/` directory before running this example.

```python
from pathlib import Path
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
Path('output').mkdir(exist_ok=True)
for source in Path('input').glob('*.html'):
    parser.parse_html_file(source, Path('output') / source.with_suffix('.docx').name)
```

Each `parse_html_string()` or `parse_html_file()` call creates a new document even
when the parser is reused. Use `add_html_to_document()` to append to one document.

## Stylesheets and selectors

```python
from mathml2docx import MathmlToDocx

stylesheets = {'theme.css': '.notice {color:navy} p > strong {color:teal}'}
parser = MathmlToDocx(
    stylesheet='h1 {font-size:20pt}',
    stylesheet_loader=stylesheets.__getitem__,
)
document = parser.parse_html_string('''
<link rel="stylesheet" href="theme.css">
<style>.notice {background-color:rgba(255,200,0,.25)}</style>
<h1>Notice</h1><p class="notice">Important <strong>content</strong></p>
''')
document.save('styled.docx')
```

The cascade handles selectors, specificity, source order, inheritance, inline
styles, and `!important`. `@media print` and `all` are applied. External `<link>`
and `@import` sources require an explicit loader. Only the Word properties in the
support table below are applied; Flexbox, Grid, JavaScript, and pixel-perfect
browser reproduction are not provided.

## Inline markers and bookmarks

Prepare `template.docx` with exactly one `{{customer}}` marker and a Word bookmark
named `result`. This example replaces those existing locations; the
[marker](examples/15_markers.md) and [bookmark](examples/16_bookmarks.md) examples
also show how to create the starting document in Python.

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
document = Document('template.docx')
parser.replace_html(document, '{{customer}}', '<b>Alex</b>')
parser.replace_bookmark(document, 'result', '<h2>Analysis</h2><p>Details</p>')
document.save('filled.docx')
```

A unique marker can span runs. Multiple occurrences are refused to avoid changing
unintended locations. Inline HTML stays in the paragraph; block HTML is inserted
between the surrounding text. Document bodies and table cells are supported.
Bookmarks may span one paragraph or several paragraphs in the same container;
ranges crossing table cells are refused. Existing run formatting, pictures, and
links, plus relationships for inserted HTML, are preserved. Header/footer markers
are not part of the current body search.

## Fonts and tab stops in a template

```python
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from mathml2docx import MathmlToDocx

document = Document()
normal = document.styles['Normal']
normal.font.name = 'Noto Sans CJK KR'
normal.font.size = Pt(11)
normal.paragraph_format.tab_stops.add_tab_stop(
    Cm(12), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
MathmlToDocx().add_html_to_document('<pre>Item\tAmount</pre>', document)
document.save('tabs.docx')
```

Setting a font name does not embed it; the reader's environment must provide it.
Ordinary HTML whitespace collapses. `pre` and `white-space:pre-wrap` preserve tabs
and newlines.

## Insert equation XML and handle unsupported input

```python
from docx import Document
from mathml2docx import mathml_to_omml, latex_to_omml, UnsupportedMathMLError

document = Document()
paragraph = document.add_paragraph('Calculation: ')
paragraph._p.append(mathml_to_omml('<math><msup><mi>x</mi><mn>2</mn></msup></math>'))
paragraph._p.append(latex_to_omml(r'\frac{1}{2}'))
try:
    mathml_to_omml('<math><unknown/></math>')
except UnsupportedMathMLError as error:
    print(error)  # Report unsupported content instead of silently dropping it.
document.save('equations.docx')
```

The low-level APIs return lxml OMML elements. `parse_mathml()` and `parse_latex()`
return Documents and are usually simpler. LaTeX requires its optional extra and
Python 3.6.2+. See [the supported math subset](05-migration.md).

## HTML support

| Area | Supported content |
| --- | --- |
| Structure | p, div, section, main, article, header, footer, aside, blockquote, pre, figure, figcaption, h1–h6, title |
| Text | b/strong, i/em, u, del/s/strike, sup/sub, code, span, br, hr |
| Links | External URLs, mail, internal links, id/name anchors, text in a without href |
| Tables | table, thead/tbody/tfoot, th/td, rowspan/colspan, empty merged cells, nested tables |
| Lists | ol/ul/li, start/value, nesting, independent numbering restarts |
| Images | Base64 data URLs, files below an explicit directory, asset loaders, inline width/height |
| CSS selection | Type/class/id/compound, child/sibling, static pseudo-classes, inline and important precedence |
| CSS text | color, background-color, font-family/size/weight/style, text-decoration, vertical-align |
| CSS paragraphs | text-align, margin, text-indent, line-height(%), white-space, display:none, visibility:hidden, page breaks |
| CSS tables | width, border, cell backgrounds/text/alignment, table alignment |
| Templates | Existing Document, docxtpl, class-to-paragraph/character styles, markers and bookmarks |

## CLI

```sh
python -m mathml2docx input.html output.docx
mathml2docx input.html output.docx --encoding utf-8
mathml2docx equation.tex equation.docx --format latex
mathml2docx article.md article.docx --format markdown
mathml2docx equation.mathml equation.docx --format mathml
mathml2docx input.html output.docx --force
```

Existing output is refused by default. `--force` explicitly allows overwriting;
using the input path as output is still refused. Python `Document.save()` follows
python-docx's own save behavior.

## Convert Markdown directly

```python
from mathml2docx import MathmlToDocx

# python -m pip install "mathml2docx[markdown]"
MathmlToDocx().parse_markdown("# Title\n\n~~Removed~~ and `code`").save("article.docx")
```

Tables, fenced code, and strikethrough are supported. `~~` inside code is literal.

## Korean and CJK fonts

Select a CJK font available in the reader. Examples 24–27 request Malgun Gothic.
For HTML fragments, target actual elements such as `p`, or use an inline container
style. A `body` selector requires a `<body>` element in the input.

```python
from mathml2docx import convert

convert('<div style="font-family:Malgun Gothic"><p>한글 and English</p></div>', 'korean.docx')
```

CSS font families populate Latin, East Asian, and complex-script font slots.
Font files are not embedded.
