# Equation layout and input handling

Use MathML for structured equations, or install the `latex` extra for a LaTeX frontend.
Supported expressions become editable Word equations. Unsupported visual notations
can be preserved as visible source or rendered by an application-supplied callback.

## Inline and display equations

The default for `<math>` is `inline`, as defined by [MathML](https://www.w3.org/TR/MathML3/chapter2.html#interf.toplevel).
Adjacent text and punctuation remain in the same paragraph.

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.convert('''<p>The value <math><mi>x</mi></math>, measured in metres.</p>
<math display="block"><mfrac><mn>1</mn><mn>2</mn></mfrac></math>''', 'layout.docx')
```

Display equations use a separate paragraph and an OMML `oMathPara` wrapper.
For older input that relies on omitted `display` meaning block, use
`MathmlToDocx(default_math_display='block')`.

Placement precedence is: supported CSS `display` → the MathML `display` attribute
→ `default_math_display`. Recognized CSS values are `inline`, `block`,
`inline math`, `block math` and `inline-block` (placed inline). CSS is ignored
when `styles=False`. `displaystyle` concerns mathematical styling, not paragraph
placement; it is not a substitute for `display`.
`mathml_to_omml()` returns an equation node only; its caller controls document placement.

## Native notation support

| MathML | Support |
| --- | --- |
| Tokens, rows, fractions, roots and ordinary scripts | Native OMML |
| Accents, over/underlines, limits and rectangular matrices | Native OMML within the documented attribute subset |
| `mmultiscripts` | One postscript pair and one prescript pair; `none` represents an absent script |
| `menclose` | `box`, `top`, `bottom`, `left`, `right`, `actuarial`, `radical`, horizontal/vertical/diagonal strikes |
| `menclose` circles, rounded boxes, long division or arrow enclosures | Explicit fallback required |
| Multiple prescript/postscript columns, Content MathML, chemical structure diagrams | Explicit fallback or input preprocessing required |

For chemical formulas, use upright element names (`mathvariant="normal"`),
subscripts for atom counts and superscripts for charges. `mmultiscripts` can place
atomic/mass numbers before an element. Reaction arrows and annotations can use
`mo`, `mover` and `munder`. See the [chemistry example](examples/28_chemistry_enclosures.md).
This is notation support, not a chemical parser or a LaTeX `mhchem` implementation.

## Target LibreOffice

Use `MathmlToDocx(math_target='libreoffice')` when the document will be opened in
Writer. This adds explicit upright-run properties for plain identifiers and
routes known lossy native OMML constructs through the same recovery policy.
Phantom spacing, string quoting, bevelled fractions, enclosures other than radicals
and partially empty prescripts require recovery
because Writer 24.2 can change their display, drop marks or show placeholders.

```python
parser = MathmlToDocx(math_target='libreoffice', unsupported_math='text')
```

For a faithful enclosure image, supply `mathml_fallback` instead of text recovery.
`math_target='word'` is the default and retains native editable enclosures.
The target is explicit; the converter cannot detect which application will open
a DOCX later. It is a policy for known incompatibilities, not a guarantee of
identical layout across Writer versions. The same target/recovery settings apply
to `parse_latex()`. Low-level helpers accept `target='libreoffice'` and still raise
when an image renderer is required.

## Preserve unsupported input as text

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(unsupported_math='text')
parser.parse_mathml('<math><menclose notation="circle"><mi>x</mi></menclose></math>').save('source.docx')
```

The output visibly includes `[Unconverted MathML]` and the complete XML.
It is a source representation, not an equivalent rendered equation. The formula
is not silently removed, and `MathMLFallbackWarning` identifies the recovery.
The default `unsupported_math='error'` keeps strict conversion.

## Supply an external renderer

A callback receives the normalized MathML source and `UnsupportedMathMLError`.
Return a nonempty string for literal text, or PNG/JPEG image bytes / `BytesIO`
for a rendered image. An image is embedded in the document and limited to the
available page width. Its alternative text uses `alttext`, or the MathML source
when no alternative text exists. Images are not editable equations.

```python
from mathml2docx import MathmlToDocx

def fallback(source, error):
    # Connect your trusted MathML renderer here. This example preserves source.
    return 'Unsupported equation: ' + source

parser = MathmlToDocx(mathml_fallback=fallback)
parser.parse_mathml('<math><unknown/></math>').save('recovered.docx')
```

The callback takes priority over `unsupported_math`. It is invoked only for
unsupported MathML conversion; malformed XML, invalid argument counts and
application callback errors still propagate. Empty or invalid callback results
are errors. No rendering service is contacted automatically.
See the [complete image fallback example](examples/29_math_fallbacks.md).

## Normalize input before conversion

`mathml_preprocessor(source)` runs once per formula in HTML and standalone MathML.
Return a complete MathML string. Both the original and returned XML are parsed
without DTDs, entity expansion or network access.

```python
from lxml import etree
from mathml2docx import MathmlToDocx

def normalize(source):
    root = etree.fromstring(source.encode('utf-8'))
    if root.get('data-display') == 'separate':
        root.set('display', 'block')
    return etree.tostring(root, encoding='unicode')

parser = MathmlToDocx(mathml_preprocessor=normalize)
parser.convert('<math data-display="separate"><mi>x</mi></math>', 'normalized.docx')
```

Preserve mathematical meaning when normalizing; removing an unknown tag can lose
its notation. Use an image renderer when exact visual preservation matters.
