# Validation and remaining limitations

Checks were performed on 2026-11-10 and extended on 2026-11-11 and 2026-11-12. This page records
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

The official schema check covers 302 corpus entries (20 + 24 + 240 + 18), the bodies
of 27 examples, and their 198 embedded equations. An invalid fraction is a negative
control. Only unused `mc:Ignorable` metadata is removed from body validation;
unknown extensions are not silently filtered. This is not certification of every
part in a complete DOCX package.

Nine targeted converter mutations are detected: numerator/denominator exchange,
radical degree/body exchange, subscript/superscript exchange, restoring a binomial
bar, losing a mathvariant, delimiter, or accent, collapsing adjacent delimiter
groups, and detaching a LaTeX grouped power. Saved-file corruption checks
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

## Advanced inputs and real Word checks (2026-11-12)

[Research report](examples/25_research_report.md), [template workbook](examples/26_template_workbook.md),
and [advanced LaTeX report](examples/27_advanced_latex.md) add 18 distinct authored
inputs: 10 MathML and 8 LaTeX. They cover a 3×3 Hessian, matrices inside matrix
cells, Schur complements, a six-level continued fraction, piecewise expressions,
double sums, normalized derivatives, and grouped powers. Input files are under
`examples/assets/advanced-math/`; independent answers are in
`tests/fixtures/advanced_math_expectations.json`. The workbook reuses the ten
MathML cases in a different layout; these are not counted as ten new formulas.

These checks found and fixed three issues: adjacent matrix delimiters were grouped
around the whole expression, powers following a closing parenthesis did not retain
the complete grouped base, and a prefixed cases table from latex2mathml 3.64 lacked
its own left delimiter. The expanded suite also passes on actual Python 3.6.

Locally installed Windows Microsoft Word **16.0** opened all **27** generated
examples read-only, exported PDFs, and saved separate DOCX copies. Their **198**
equations retained their mathematical roles. Word rewrites Unicode minus U+2212
to ASCII hyphen-minus when saving; only this math-text spelling is normalized in
the Word persistence comparison. Converter-to-answer tests retain strict Unicode
comparison. Other roles, matrix dimensions, delimiters, and script bases remain exact.

For examples 24–27, the saved copies also match selected text/order, emphasis,
colors, list starts, merged/nested tables, image hashes/dimensions, and link targets.
Word style IDs are compared through their declared style names. Display-equation
wrappers, proofing marks and derived `lastRenderedPageBreak` markers carry no
content in this comparison; explicit HTML line/page breaks remain checked.
The comparison is a saved-structure check, not an interactive editing or visual
certification. Selected PDF pages were inspected; exported text boxes in examples
24–27 remained within page bounds. Not every glyph or page has been reviewed.

Reproduce on Windows or WSL with desktop Word installed (source files stay read-only;
use a fresh output directory because existing review files are refused):

```sh
python scripts/check_word.py --input examples/output --output examples/output/word-review
python scripts/check_word.py --input examples/output --output examples/output/word-mixed-review --examples 24_dense_report 25_research_report 26_template_workbook 27_advanced_latex --check-blocks
```

Word is optional validation tooling, not a runtime dependency or a CI prerequisite.
Strict `--check-blocks` may flag equivalent serialization in other documents, such
as Word dropping an explicit underline `none`; those differences require review.

## Korean and other East Asian text

Examples 24–27 explicitly request **Malgun Gothic** (맑은 고딕). CSS `font-family`
now sets East Asian and complex-script font slots as well as Latin slots.
No font is forced when the input omits a font family; template defaults still apply.
Font files are not embedded or bundled. Other systems/readers need an installed
font containing the required glyphs, or an available CJK font selected in the example.

The reported square-glyph symptom was not reproduced with the original example 24
in local Word 16; its stored Korean text was intact. The explicit font mapping is
now tested in saved DOCX files and the revised Word-rendered output displays Korean.
The reporting application's font fallback still needs confirmation if squares persist.

## Outstanding coverage

The Word 16 automation above covers opening, PDF export, and resaving on one
Windows installation. Interactive editing, accessibility, Word web/macOS, and
other Word versions remain unverified. LibreOffice is not a substitute for these
checks. Fonts/readers may change line height, wrapping, and pagination.

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
