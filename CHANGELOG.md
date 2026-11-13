# Changelog

## 1.0.1 — 2026-11-14

### Conversion fixes

- Preserve encoded mathematical alphabets under explicit or inherited
  `mathvariant`, including mixed tokens and literal strings. Keep styled
  `mtext`/`ms` spacing literal when Word imports or resaves an equation.
- Reject unresolved LaTeX command tokens instead of saving them as formula
  identifiers; preserve explicit text and real backslash symbols.

### Documentation

- Use published PyPI installation commands throughout English/Korean READMEs,
  getting started, migration, recipe and example guides.
- Run the downloadable example bundle with the installed package and explicit
  optional dependencies; document source checkout and uv commands for contributors.
- Update release status and verify examples outside the source checkout.
- Use absolute README links for PyPI and include package-installation checks in
  the documented release checklist.

## 1.0.0 — 2026-11-13

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

- Honor scoped MathML defaults, compact movable limits, XML whitespace, Unicode input
  declarations and quoted strings. Validate known arities before unsupported-element recovery.
- Recover explicitly for unsupported merged/ragged matrices, forced breaks, RTL and complex
  accents instead of silently changing their meaning. Preserve supported MathML CSS and anchors.
- Preserve equations around template markers and within bookmark replacement boundaries.
- Preserve linked display equations and mixed math styles through Word resaving; align
  native OMML properties with Unicode mathematical alphabets already emitted by LaTeX backends.

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
- Check independently authored source equation counts before rendering, compare math run
  styles and explicit display layout, and detect lost internal-link targets.
- Verify LibreOffice formula import counts and a real PDF math probe; fail when Math is missing.
  Add a dedicated CI job and explicit Writer/Math/font setup instructions.

- Add text equation inputs and independent JSON answers for inspecting saved DOCX structures.
- Add 30 runnable examples, schema validation, mixed-document checks, and targeted corruption tests.
- Provide English-default and Korean READMEs and documentation, with equivalent-page
  language switching and localized search.
- Add 18 advanced authored inputs with independent answers and optional Windows
  Word open/PDF-export/resave checks, with 224 native equations across 30 examples.
- Exclude XSL and generated DOCX files from new package distributions; retain inherited MIT notices.
- Manage dependencies with uv and verify legacy/modern Python plus Windows/macOS in CI.
- Use develop for daily work, master pushes for unique TestPyPI candidates and remote
  installation checks, and verified final tags for PyPI publishing through OIDC.

Historical XSL redistribution rights and application-specific visual review remain separate concerns.
See the migration, licensing and validation guides for compatibility and distribution limits.
