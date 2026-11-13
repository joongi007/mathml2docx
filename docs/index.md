# HTML and equations, ready for Word

Build Word documents from Python strings, files and document templates.
mathml2docx converts supported HTML and MathML into formatted text and editable Word equations.

## Start with a document

Install the published package from PyPI:

```sh
python -m pip install mathml2docx
```

```python
from mathml2docx import convert

convert('<h1>Lesson notes</h1><p>The value <math><mi>x</mi></math> is editable.</p>',
        'lesson.docx')
```

Install the package and run this example with the [getting started guide](01-getting-started.md).
Microsoft Office is not required for conversion.

## Choose your workflow

| Your input | Where to start |
| --- | --- |
| HTML with text, tables or images | [Getting started](01-getting-started.md) and [formatting recipes](08-recipes.md) |
| MathML or LaTeX equations | [Equation layout and input handling](03-mathematics.md) |
| An existing Word template | [Markers](examples/15_markers.md), [bookmarks](examples/16_bookmarks.md) and [docxtpl](examples/17_docxtpl.md) |
| A scientific report or worksheet | [Research report](examples/25_research_report.md) and [template workbook](examples/26_template_workbook.md) |
| Chemistry or nonstandard mathematics | [Chemical notation](examples/28_chemistry_enclosures.md) and [fallback rendering](examples/29_math_fallbacks.md) |
| Code using mathml2docx 0.x | [Migration guide](05-migration.md) |

## Understand the output

Equations use Word's native OMML format, so supported formulas remain editable.
HTML and CSS support is selective; browser layouts, arbitrary MathML notations and
LaTeX packages are not all reproduced. Use explicit recovery for unsupported input
and review the [application compatibility guide](11-validation.md) for fonts and LibreOffice.

Browse [all examples](examples/00-index.md) for complete Python code, DOCX downloads
and PDF previews, or consult the [API reference](02-api.md) for individual options.
