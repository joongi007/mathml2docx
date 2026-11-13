# MathML equations

Create editable fractions, scripts, indexed roots, delimiters, matrices, and inline equations.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.13_mathml
```

[Generated DOCX](../downloads/examples/13_mathml.docx)

[Reference PDF](../assets/previews/13_mathml.pdf)

## Complete source

```python
"""13 mathml example."""

from mathml2docx import MathmlToDocx

from .support import save

parser = MathmlToDocx()
document = parser.parse_mathml("<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>")
parser.add_html_to_document(
    """<h2>Inline and block math</h2><p>Area:
<math display="inline"><mi>A</mi><mo>=</mo><mi>π</mi><msup><mi>r</mi><mn>2</mn></msup></math>.</p>
<math><mroot><mi>x</mi><mn>3</mn></mroot><mo>+</mo><msubsup><mi>x</mi><mn>1</mn><mn>2</mn></msubsup></math>
<math><mfenced open="[" close="]"><mtable><mtr><mtd><mn>1</mn></mtd><mtd><mn>2</mn></mtd></mtr><mtr><mtd><mn>3</mn></mtd><mtd><mn>4</mn></mtd></mtr></mtable></mfenced></math>""",
    document,
)
save(document, "13_mathml.docx")
```
