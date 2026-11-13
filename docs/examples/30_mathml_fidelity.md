# MathML notation and document fidelity

Inherited defaults, inline/display sums, composite scripts, equation-safe templates, cell layout, CSS and Unicode.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.30_mathml_fidelity
```

[Generated DOCX](../downloads/examples/30_mathml_fidelity.docx)

[Reference PDF](../assets/previews/30_mathml_fidelity.pdf)

## Complete source

```python
"""MathML defaults, accents, document insertion and styles in one document."""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx, TableStyle, mathml_to_omml

from .support import save

parser = MathmlToDocx(table_style=TableStyle.GRID)
document = Document()
parser.add_html_to_document(
    "<h1>Mathematical notation and document layout</h1>"
    "<p>Editable formulas with explicit inline/display choices, inherited defaults, "
    "styles and existing document content. 수식과 본문 서식을 함께 사용합니다.</p>",
    document,
)

# Eight independent expressions. Default MathML is inline; display is explicit.
expressions = [
    (
        "Binomial coefficient",
        '<math display="block" linethickness="0"><mfenced><mfrac><mi>n</mi><mi>k</mi></mfrac></mfenced></math>',
    ),
    (
        "Closed interval",
        '<math display="block"><mstyle open="[" close="]"><mfenced><mi>a</mi><mi>b</mi></mfenced></mstyle></math>',
    ),
    (
        "Adjacent factors",
        '<math display="block"><mstyle separators=""><mfenced><mi>a</mi><mi>b</mi></mfenced></mstyle></math>',
    ),
    (
        "Upper and lower rules",
        '<math display="block"><munderover accentunder="true" accent="true"><mrow><mi>x</mi><mo>+</mo><mi>y</mi></mrow><mo>_</mo><mo>¯</mo></munderover></math>',
    ),
    (
        "Compact summation",
        "<p>Inside a sentence: <math><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msub><mi>a</mi><mi>i</mi></msub></math>, with side limits.</p>",
    ),
    (
        "Display summation",
        '<math display="block"><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msub><mi>a</mi><mi>i</mi></msub></math>',
    ),
    (
        "Composite overscript",
        '<math display="block"><mover accent="false"><mi>x</mi><msqrt><mi>y</mi></msqrt></mover></math>',
    ),
    (
        "Styled ratio",
        '<p style="color:#9c2745;font-size:24pt">Ratio: <math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>.</p>',
    ),
]
for title, html in expressions:
    parser.add_html_to_document("<h2>" + title + "</h2>" + html, document)

parser.add_html_to_document("<h2>Insert between existing equations</h2>", document)
paragraph = document.add_paragraph()
paragraph._p.append(mathml_to_omml("<math><mi>x</mi></math>"))
paragraph.add_run(" {{result}} ")
paragraph._p.append(mathml_to_omml("<math><mi>z</mi></math>"))
parser.replace_html(document, "{{result}}", "<math><mi>y</mi></math>")

parser.add_html_to_document("<h2>Replace a bookmarked result</h2>", document)
paragraph = document.add_paragraph("Selected result: ")
start, end = OxmlElement("w:bookmarkStart"), OxmlElement("w:bookmarkEnd")
start.set(qn("w:id"), "42")
start.set(qn("w:name"), "chosen_result")
end.set(qn("w:id"), "42")
paragraph._p.extend([start, mathml_to_omml("<math><mi>u</mi></math>"), end])
parser.replace_bookmark(document, "chosen_result", "<math><mi>v</mi></math>")

parser.add_html_to_document("<h2>Display equations in a table cell</h2>", document)
cell = document.add_table(rows=1, cols=1).cell(0, 0)
parser.add_html_to_cell(
    '<math display="block"><mi>p</mi></math><math display="block"><mi>q</mi></math><p>Two separate display equations, followed by text.</p>',
    cell,
)

parser.add_html_to_document("<h2>Unicode and string literals</h2>", document)
paragraph = document.add_paragraph("Unicode label: ")
paragraph._p.append(
    mathml_to_omml(
        '<?xml version="1.0" encoding="ISO-8859-1"?><math mathvariant="normal"><mtext>café: 𝐱 + ℝ</mtext></math>'
    )
)
parser.add_html_to_document(
    "<p>A string with quotation marks: <math><ms>say &quot;yes&quot;</ms></math>.</p>",
    document,
)

parser.add_html_to_document(
    '<h2>Equation links</h2><p><a href="#ratio_result">Jump to the ratio</a>.</p><math id="ratio_result" display="block"><mfrac><mn>1</mn><mn>2</mn></mfrac></math><p><a href="https://example.com/method">Method: <math display="block"><mfrac><mrow><mi>x</mi><mo>+</mo><mi mathvariant="bold">z</mi></mrow><mi mathvariant="normal">N</mi></mfrac><mo>∈</mo><mi mathvariant="double-struck">R</mi></math>continued reference</a>.</p>',
    document,
)
save(document, "30_mathml_fidelity.docx")
```

## Visual comparison notes

This DOCX targets Word. LibreOffice can misparse quoted `ms` strings, omit text or show a formula error in this PDF preview. For LibreOffice output, select `math_target='libreoffice'` and source/image recovery; native `ms` is rejected for that target.

[Validation scope and limitations](../11-validation.md)
