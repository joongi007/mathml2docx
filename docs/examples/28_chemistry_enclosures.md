# Chemical notation and enclosures

Upright element symbols, isotope prescripts, charges, reaction arrows and native enclosures.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.28_chemistry_enclosures
```

[Generated DOCX](../downloads/examples/28_chemistry_enclosures.docx)

[Reference PDF](../assets/previews/28_chemistry_enclosures.pdf)

## Complete source

```python
"""Chemical equations, isotope scripts, and native mathematical enclosures."""

from mathml2docx import TableStyle, convert

from .support import save

html = """<html><body>
<style>body {font-family:'Malgun Gothic';font-size:11pt} h1,h2 {color:#17365d}</style>
<h1>Chemical notation / 화학 표기</h1>
<p>Atom counts and ionic charges use separate scripts. Element symbols remain upright.</p>
<p>Water / 물: <math><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mi mathvariant="normal">O</mi></math>.</p>
<p>Sulfate ion / 황산 이온: <math><msubsup><mrow><mi mathvariant="normal">S</mi><mi mathvariant="normal">O</mi></mrow><mn>4</mn><mrow><mn>2</mn><mo>−</mo></mrow></msubsup></math>.</p>
<h2>Isotopes / 동위원소</h2>
<math display="block"><mmultiscripts><mi mathvariant="normal">C</mi><none/><none/><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts><mo>→</mo><mmultiscripts><mi mathvariant="normal">N</mi><none/><none/><mprescripts/><mn>7</mn><mn>14</mn></mmultiscripts><mo>+</mo><mmultiscripts><mi mathvariant="normal">e</mi><none/><none/><mprescripts/><mrow><mo>−</mo><mn>1</mn></mrow><mn>0</mn></mmultiscripts></math>
<h2>Reaction conditions / 반응 조건</h2>
<math display="block"><mn>2</mn><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mo>+</mo><msub><mi mathvariant="normal">O</mi><mn>2</mn></msub><mover accent="false"><mo>→</mo><mtext>heat</mtext></mover><mn>2</mn><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mi mathvariant="normal">O</mi></math>
<h2>Enclosures / 수식 테두리</h2>
<table><tr><th>Notation</th><th>Editable expression</th></tr>
<tr><td>Box</td><td><math><menclose notation="box"><mfrac><mi>a</mi><mi>b</mi></mfrac></menclose></math></td></tr>
<tr><td>Cancellation</td><td><math><menclose notation="updiagonalstrike"><mi>x</mi></menclose><mo>+</mo><mn>1</mn></math></td></tr>
<tr><td>Top and right (actuarial)</td><td><math><menclose notation="actuarial"><mi>n</mi></menclose></math></td></tr>
<tr><td>Radical</td><td><math><menclose notation="radical"><mi>x</mi><mo>+</mo><mn>1</mn></menclose></math></td></tr></table>
<p>These formulas use native Word equations. Chemical structure diagrams require a separate renderer. For LibreOffice, choose math_target=libreoffice with image recovery for enclosures; Writer can omit native Word borders.</p>
</body></html>"""
save(convert(html, table_style=TableStyle.GRID), "28_chemistry_enclosures.docx")
```
