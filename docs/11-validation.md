# Compatibility and validation

Generated documents use standard WordprocessingML and OMML. Conversion tests check
saved content against independently written answers and official XML schemas.
Document applications can still differ in fonts, equation layout and pagination.

## What is checked

| Check | Purpose | Limit |
| --- | --- | --- |
| Independent equation answers | Fractions, script roles, radicals, matrices, delimiters, variants and content | Does not compare pixels or interactive editing |
| Saved-document checks | Text order, math styles/layout, tables, merges, numbering, images and link targets | Covers selected properties |
| Official ECMA-376 schemas | Valid OMML and body element ordering | Valid structure is not proof of intended meaning |
| Mutation checks | Verify that representative equation damage is detected | Not every possible defect |
| Word automation | Open, export and resave example documents with Word 16 | One installed Word environment |
| LibreOffice checks | Count imported formula objects and test actual PDF math output | Layout can differ from Word |

The source corpus contains 44 manually authored base equations, 240 seeded
combinations and 18 advanced inputs. The seeded set has 210 distinct input strings,
including simple tokens; these are not 240 different complex reports. Advanced
examples include nested block matrices, six-level continued fractions, integrals,
partial derivatives, scientific prose, tables and images.

Inputs live in `examples/assets/math-corpus/` and `examples/assets/advanced-math/`.
Independent answers live in `tests/fixtures/`; generated DOCX is not kept in Git.
[Examples](examples/00-index.md) provide files suitable for manual review. The 30
runnable examples contain 224 native equations;
[example 30](examples/30_mathml_fidelity.md) adds independent answers for inherited
defaults, compact/display limits, accents, CSS and template replacement.

Before rendering, each generated document must match the separately authored
`tests/fixtures/example_equation_counts.json` manifest. Counting only the formulas
already present in a DOCX would miss equations lost during conversion. Checks
also distinguish inline/display layout, effective math variants, nonbreaking
spaces, colors, sizes and fonts. Internal hyperlinks must have bookmark targets.

## Fonts

The converter references fonts; it does not embed font files. Install fonts that
contain the characters used in the document. An unavailable font or incomplete
fallback can produce square glyphs, especially for CJK and mathematical alphabets.

CSS `font-family` applies to Latin, East Asian and complex-script font slots.
Without an explicit font, the Word template's defaults apply. Examples 24–28 use
Malgun Gothic; on other systems select an installed CJK font, such as Noto Sans CJK.
Neither font is bundled with the Python package.

## LibreOffice

Install both **Writer and Math**. A minimal Writer-only installation may import
text while leaving all equations blank, even when PDF export exits successfully.
This was reproduced on LibreOffice 24.2.7.2; adding Math restored visible formulas
in the same files. CJK and math fonts must also be available.

On Debian/Ubuntu:

```sh
sudo apt-get install libreoffice-writer libreoffice-math poppler-utils fonts-noto-cjk fonts-stix
```

To reproduce previews and automated checks, prepare a source checkout using
[the development setup](09-development-release.md). Run these commands from its root:

```sh
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/render_examples.py --output examples/output/libreoffice-review
```

The check uses fresh temporary outputs, verifies formula counts in LibreOffice's
flat XML export, and requires a PDF text probe to confirm actual math rendering.
Missing or empty equations cause failure. `pdftotext` is required; pass
`--soffice` and `--pdftotext` if they are not on PATH. Existing outputs require
`--force` before replacement.

Writer 24.2 can also omit native OMML borders and cancellation marks. Select
`math_target='libreoffice'` to route those constructs through explicit recovery,
and to preserve upright chemical element names. Empty postscript pairs are
omitted to avoid placeholder squares. The default Word-target chemistry preview
illustrates the remaining enclosure difference; use image recovery when needed.

Native equations are not automatically replaced by images for a particular viewer.
For unsupported input, choose [explicit source or image recovery](03-mathematics.md).
An image is useful when a fixed appearance matters more than editability.

### Known display differences

Phantom spacing, bevelled fractions, string quoting, accents and line wrapping can
vary between document applications. Phantom content is intentionally hidden;
reserved dimensions may differ. A skewed fraction can appear as a stacked fraction
in LibreOffice. Compare the equation gallery with its input when these features
matter. Structure checks do not certify visual equivalence.

LibreOffice can misparse quoted `ms` strings in Word-target documents, omit part
of the text or show a formula error. This is a content-loss limitation, not just
font substitution. `math_target='libreoffice'` rejects native `ms` before output;
select explicit source or image recovery for those strings. Example 30's PDF
illustrates this viewer limitation; its DOCX is intended for Word.

## Reproduce the automated checks

```sh
uv run --no-sync python -m pytest -q
uv run --no-sync python scripts/check_math_mutations.py
uv run --no-sync python scripts/prepare_ecma_schema.py /tmp/mathml2docx-ecma376
uv run --no-sync python scripts/validate_math_schema.py --schemas /tmp/mathml2docx-ecma376
```

Schemas come from [ECMA-376](https://ecma-international.org/publications-and-standards/standards/ecma-376/)
and [W3C xml.xsd](https://www.w3.org/2001/xml.xsd), with hashes checked by the preparation script.
They are not distributed in the package.

On Windows or WSL with Word installed:

```sh
python scripts/check_word.py --input examples/output --output examples/output/word-review
python scripts/check_word.py --input examples/output --output examples/output/word-mixed-review --examples 24_dense_report 25_research_report 26_template_workbook 27_advanced_latex --check-blocks
```

The tool opens inputs read-only and saves separate copies. Word may rewrite the
Unicode minus U+2212 as ASCII hyphen-minus; only the Word resave comparison accepts
that spelling difference inside math sequences. Independent converter answers
remain Unicode-exact. The report separates raw serialization changes from
effective differences. It resolves inherited formatting and known font-name
aliases, then checks every originally declared math color, size, font and
bold/italic property. Math script-family metadata on symbols without mathematical alphabet
variants (such as `+` and `∈`) can be omitted from the effective comparison.
Letters, digits and mapped symbols such as `∂` and `∇` remain exact. Word can wrap an isolated math-only paragraph as display math;
that change is listed separately. An explicitly displayed equation becoming
inline still fails. Word web, macOS Word, accessibility and interactive equation
editing require separate review in the target environment.
