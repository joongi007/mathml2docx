# Changelog

## 1.0.0 — Unreleased

### Conversion and integration

- Replace the bundled Office XSL with a native Presentation MathML-to-OMML converter.
- Rework HTML traversal for merged/nested tables, inline assets, lists, links, and static CSS.
- Add optional LaTeX/Markdown frontends, a CLI, public Word style constants, class mappings,
  and marker/bookmark replacement in existing documents.
- Preserve the Python 3.6 core runtime. LaTeX requires Python 3.6.2+ and latex2mathml 3.64+.
- Preserve adjacent matrix fence groups, complete parenthesized script bases, and
  prefixed cases on older LaTeX backends. Apply explicit CSS fonts to East Asian
  and complex-script slots as well as Latin text.
- Correct fraction types, mathematical alphabets, accents, delimiters, cases tables,
  limit grouping, per-operator layout directives, inline spacing, and OOXML property order.

- Follow MathML inline defaults, with configurable missing-display layout and CSS precedence.
- Support selected enclosures and chemical prescripts, and explicit preprocessing, source/image
  fallback, and LibreOffice compatibility policies. Avoid empty postscript placeholders.

### Compatibility changes

- URL images and external stylesheets require explicit loaders; local images are limited
  to a configured base directory.
- File conversion adds `.docx` once and returns the output Path.
- `fix_html` is retained for call compatibility; HTML always uses tree parsing.
- Style helpers require explicit run/paragraph targets. Unsupported MathML is reported
  rather than silently dropped. Full browser CSS and complete MathML/LaTeX are not promised.

### Validation and packaging

- Replace MkDocs with a custom Markdown/Jinja static site, responsive navigation, bilingual
  search and code copying. Rewrite reader-facing guides and remove session status reports.
- Verify LibreOffice formula import counts and a real PDF math probe; fail when Math is missing.
  Add a dedicated CI job and explicit Writer/Math/font setup instructions.

- Add text equation inputs and independent JSON answers for inspecting saved DOCX structures.
- Add 29 runnable examples, schema validation, mixed-document checks, and targeted corruption tests.
- Provide English-default and Korean READMEs and documentation, with equivalent-page
  language switching and localized search.
- Add 18 advanced authored inputs with independent answers and optional Windows
  Word open/PDF-export/resave checks (198 equations across 27 examples).
- Exclude XSL and generated DOCX files from new package distributions; retain inherited MIT notices.
- Manage dependencies with uv and verify legacy/modern Python plus Windows/macOS in CI.
- Use develop for daily work, master pushes for unique TestPyPI candidates and remote
  installation checks, and verified final tags for PyPI publishing through OIDC.

Historical XSL redistribution rights and application-specific visual review remain separate concerns.
See the migration, licensing, validation, and publishing documentation before release.
