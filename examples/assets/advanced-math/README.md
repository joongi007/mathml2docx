# Advanced equation inputs

These 18 original inputs are authored for this repository: 10 MathML expressions
(A01–A10) and 8 LaTeX expressions (B01–B08). The catalog gives each input a stable
ID, title, format, and source filename. No external equation corpus is copied.

The set exercises nested matrix cells, a 3×3 Hessian, a six-level continued
fraction, normalized derivatives, double sums, grouped powers, piecewise tables,
and matrix products. These are distinct expressions rather than repeated
placements of one equation. Examples 25 and 26 reuse the MathML expressions in
different document contexts; example 27 uses the LaTeX inputs.

Independent answers live in `tests/fixtures/advanced_math_expectations.json`.
They describe numerator/denominator, grouped base/scripts, matrix shape, limits,
radicals, and delimiters. They are not generated from converter output.
`tests/test_advanced_documents.py` compares saved DOCX files with those answers.

The tests establish selected mathematical and document structure, not the truth
of a symbolic identity or visual fidelity in every Word version.
