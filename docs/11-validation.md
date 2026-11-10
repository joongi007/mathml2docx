# Validation and remaining limitations

Checks were performed on 2026-11-10 and extended on 2026-11-11. This page records
evidence within the supported subset; it does not certify every MathML, LaTeX,
HTML, or Word-version combination.

## Different checks establish different facts

| Check | Establishes | Does not establish |
| --- | --- | --- |
| Mathematical role comparison | Content and positions of numerator/denominator, base/scripts, radical degree/body, and matrix cells | Font appearance, wrapping, or actual editing UX |
| ECMA-376 XSD | OMML structure, required properties, and Word body element order | Mathematical equivalence to the input or layout |
| DOCX save/reopen | Persistence of equations, tables, formatting, images, and links | Display in Microsoft Word itself |
| LibreOffice PDF | Actual rendering in an independent document application | Pixel equivalence to Word |
| Deliberate corruption | Sensitivity to representative equation/document damage | Detection of every possible defect |

Role/content answers are not generated from the converter's output. A separate
expression model is encoded as MathML and compared with roles read independently
from OMML. Official schemas provide another independent structural check.

## Compare a saved DOCX with independent answers

Generated DOCX and binary reference DOCX files are not committed. The 44 authored
inputs live as HTML/LaTeX text in `examples/assets/math-corpus/`, with stable IDs in
`catalog.json`. Python examples read the same inputs. Independently authored
answers are in `tests/fixtures/math_expectations.json`.

`tests/test_docx_oracles.py` creates temporary DOCX files through the MathML, HTML,
and LaTeX frontends. `tests/docx_oracle.py` reads the actual ZIP/XML and compares
its content with those answers without importing the converter or python-docx.
The gallery's 44 equations and mixed report's 120 placements are also checked.
Save/reopen XML equality is a separate persistence check, not an independent
answer for the original mathematical meaning.

`examples/assets/mixed_math.html` and `tests/fixtures/mixed_math_expectation.json`
check content order, emphasis, underline, color, alignment, merged/nested tables,
list start values, link targets, image hashes/dimensions, and line breaks.
Deliberately altered numerators, formatting, relationships, numbering, merges,
and matrix dimensions must disagree with the answers.

```sh
uv run --no-sync python -m unittest tests.test_docx_oracles -v
```

The repository's `tests/fixtures/README.md` explains the representation and ignored
incidental differences. This checks selected saved structures/properties, not
Word's rendered page layout.

The 2026-11-11 checks exposed latex2mathml 3.64's handling of `\nolimits`, a global
limits setting that incorrectly affected other operators, and a cases table's
left brace. Layout directives now apply per operator and remain literal inside
text groups. latex2mathml 2.16 disagrees with several text/accent/spacing answers
and is no longer supported. HTML/MathML retains Python 3.6.0+ support; optional
LaTeX requires Python 3.6.2+ and latex2mathml 3.64+.

## Equations and mixed documents

The [corpus source](https://github.com/joongi007/mathml2docx/blob/master/examples/math_corpus.py)
and text input files are included in the repository and example ZIP.

- 20 authored MathML cases: quadratic roots, continued fractions, binomial
  coefficients, nested roots, tensor scripts, series, improper integrals,
  derivatives, matrices, piecewise expressions, accents, limits, probability,
  math alphabets, annotations, and phantom.
- 24 LaTeX cases: related constructs plus large delimiters, text, explicit spacing,
  and `\nolimits`. Some mathematical topics overlap with the MathML cases.
- 240 deterministic generated cases with seed `376`, checked both with and without
  an XML namespace. Fractions, radicals, scripts, matrices, delimiters, limits,
  and phantom are composed to depth four. There are 210 distinct generated input
  strings; 38 cases are standalone tokens. These are not 240 distinct complex documents.
- An automated mixed document has 280 equations, 20 outer and 20 nested tables,
  20 images/links each, merged cells, numbered lists, and emphasis. Reopened content
  is checked for count, order, and mathematical roles.
- Separate boundaries include 32 nested radicals, 1,025 tokens, invalid arity or
  matrices, unknown elements/namespaces, DTD/entities, and unsupported layouts.
- [Complex equation gallery](examples/23_complex_equations.md): authored 20 MathML
  and 24 LaTeX cases, source, generated DOCX, and a reference PDF.
- [Equation-heavy report](examples/24_dense_report.md): 120 equation placements
  with tables, lists, images, multilingual text, and page breaks. Placements repeat
  the authored cases rather than adding 120 new mathematical examples.

The official schema check covers 284 corpus entries (20 + 24 + 240), the bodies
of 24 examples, and their 170 embedded equations. An invalid fraction is a negative
control. Only unused `mc:Ignorable` metadata is removed from body validation;
unknown extensions are not silently filtered. This is not certification of every
part in a complete DOCX package.

Seven targeted converter mutations are detected: numerator/denominator exchange,
radical degree/body exchange, subscript/superscript exchange, restoring a binomial
bar, and losing a mathvariant, delimiter, or accent. Saved-file corruption checks
also detect altered image bytes, links, formatting, lists, merges, and a 2×2 matrix
changed into a 1×4 matrix with the same flattened cell order.

## Fixes found by these checks

- Binomial bars, bevelled fraction type, explicit/inherited mathvariant, and string quotes.
- Operator-child accent flags, over/underlines, and explicit OMML delimiters.
- LaTeX limit position/argument grouping, text/spacing, and per-operator layout directives.
- Comments/processing instructions, empty/invalid matrices, foreign namespaces,
  and preventing loss of bare text in structural MathML.
- Whitespace after inline math, required `w:val` on shading, and table border order.

## Reproduce

Prepare the [uv development environment](09-development-release.md), then run:

```sh
uv run --no-sync python -m pytest -q
uv run --no-sync python scripts/check_math_mutations.py
uv run --no-sync python -m examples.run_all

# Download schemas only to a temporary directory; hashes are pinned.
uv run --no-sync python scripts/prepare_ecma_schema.py /tmp/mathml2docx-ecma376
uv run --no-sync python scripts/validate_math_schema.py --schemas /tmp/mathml2docx-ecma376

# Requires a separate LibreOffice installation.
uv run --no-sync python scripts/render_examples.py
```

The schemas come from `OfficeOpenXML-XMLSchema-Transitional.zip` in the official
[ECMA-376 Part 4 distribution](https://ecma-international.org/publications-and-standards/standards/ecma-376/)
and [W3C xml.xsd](https://www.w3.org/2001/xml.xsd). Original schema bytes are not
modified or bundled. Download URLs/hashes are in the preparation script; individual
schema hashes are printed by the validator. CI repeats the schema checks after
example generation.

## Outstanding coverage

Direct Microsoft Word desktop/web/macOS opening, editing, resaving, and
accessibility checks have not been performed. LibreOffice is not a substitute for
those checks. Fonts/readers may change line height, wrapping, and pagination.

In LibreOffice 7.3, the valid `skw` fraction property rendered as a regular fraction.
Phantom reserved width and ASCII quotes in `ms` also differed from the intended
display. The XML retains those structures/properties/characters, but visual
agreement remains unverified. Compare gallery M17, M19, and M20 against their
intended expressions; do not treat the reference PDF as the correct answer for them.

`menclose`, `mmultiscripts`, Content MathML, arbitrary negative spacing, forced
math line breaks, and dimensioned `mpadded` are unsupported and reported as errors.
Supported `mspace` widths use Unicode space approximations. Matrix alignment,
operator dictionaries, equation CSS, and other presentation attributes are not
fully reproduced; some are approximated or ignored. See [support scope](05-migration.md).
Very wide equations may need application-specific line breaks or page widths.

LaTeX support also depends on the installed supported backend. Checks include the
Python 3.6-compatible backend, but not every TeX environment, package, or macro.
Add real work documents with independent mathematical expectations and direct
Word inspection as further regression cases.
