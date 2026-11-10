# Independent DOCX answers

Do not commit generated DOCX or binary reference DOCX files. Keep reproducible
text inputs, independently written JSON answers, and comparison code.

| Material | Location | Purpose |
| --- | --- | --- |
| 20 MathML inputs | `examples/assets/math-corpus/M01.html`–`M20.html` | Readable MathML HTML fragments |
| 24 LaTeX inputs | `examples/assets/math-corpus/L01.tex`–`L24.tex` | Original equations |
| Input catalog | `examples/assets/math-corpus/catalog.json` | Stable IDs, titles, and filenames |
| Equation answers | `tests/fixtures/math_expectations.json` | Expected roles and selected explicit font properties |
| Mixed input | `examples/assets/mixed_math.html` | Formatting, tables, lists, links, images, inline equations |
| Mixed answer | `tests/fixtures/mixed_math_expectation.json` | Content order, styles, list starts, merges, relationships, image hashes/dimensions |
| DOCX reader | `tests/docx_oracle.py` | Read actual document XML, relationships, numbering, and images from ZIP |
| Tests | `tests/test_docx_oracles.py` | Generate temporary DOCX, compare answers, and clean up |

```sh
uv run --no-sync python -m unittest tests.test_docx_oracles -v
```

Unittest discovery runs the checks in CI, including Python 3.6. LaTeX requires
Python 3.6.2+ and latex2mathml 3.64+; HTML/MathML retains early Python 3.6 support.
The reader uses standard XML/ZIP tools without importing the converter or python-docx.

## What an answer means

For example, an answer for the fraction 1/2 can be expressed as:

```json
{
  "math": [
    {"fraction": [["1"], ["2"]], "type": "bar"}
  ]
}
```

Roles distinguish numerator/denominator, base/scripts, radical degree/body,
delimiter characters, accents, matrix rows/columns, and phantom visibility/dimensions.
Matrices are not flattened. Fixed-size parentheses stored as character runs and
growing delimiters stored as objects remain distinguishable.

For role comparison, Unicode mathematical alphabets are NFKC-normalized and
pure spacing runs are omitted. This alone does not verify font distinctions or
precise spacing. Selected `run_properties` separately require matching fields on
an actual run: MathML styles/text properties and LaTeX L15's double-struck R/bold x.
Additional properties are tested by `tests/test_math_validation.py`.

Answers are authored from the intended input meaning. They are not automatically
created from the converter output or copied from failing actual results.
Existing before/after XML comparisons check persistence, a different property.

## Incidental and meaningful differences

ZIP timestamps, relationship IDs, and equivalent run partitioning are ignored.
Relationships are compared by actual targets and image byte hashes. Mandatory
empty cell paragraphs are omitted for these inputs. This is a check of selected
content/properties, not every OOXML property or Word page layout.

Negative controls change the saved numerator, bold, hyperlink target, image bytes,
list start, merge, and heading style. Another changes a 2×2 matrix into 1×4 while
preserving flattened cell order. These changes must disagree with the answers.

## Inspect locally

```sh
uv run --no-sync python -m examples.23_complex_equations
uv run --no-sync python -m examples.24_dense_report
```

Outputs go to `examples/output/`. That directory and `*.docx` are excluded from
Git and source distributions. Distribution checks enforce this policy. Passing
structural checks does not replace direct Word display/edit/save inspection.
