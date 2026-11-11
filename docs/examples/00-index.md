# Runnable examples

The documentation build executes 27 Python examples to generate DOCX downloads.

```sh
uv sync --locked --extra latex --extra markdown --group docs --group examples
uv run --no-sync python -m examples.run_all
```

Run from a repository checkout after installing the dependencies above. Local outputs go to `examples/output/`. Run an individual example with, for instance, `python -m examples.01_quickstart`.

[All example source and assets (ZIP)](../downloads/mathml2docx-examples.zip)

The reference PDFs were rendered with LibreOffice 7.3.7. They are historical previews, not automatically refreshed by this build; Word versions and fonts may produce different results.

- [Quick start](01_quickstart.md): Save HTML with one convert() call and receive a Document.
- [Files, encoding, and Unicode](02_files_unicode.md): Use UTF-8 input, Korean/Japanese/accented text, and exact output extensions.
- [Existing documents and cells](03_existing_document.md): Append content to a Document and insert HTML into table cells.
- [Inline formatting and colors](04_inline_formatting.md): Apply emphasis, underline, strike, scripts, code, and alpha-composited colors.
- [CSS stylesheets](05_stylesheets.md): Combine style tags, explicit external CSS loading, selectors, inheritance, and important precedence.
- [Word styles and class mapping](06_word_styles.md): Map HTML classes to public style constants and custom character styles.
- [Paragraph layout and page breaks](07_page_layout.md): Set alignment, spacing, indentation, line height, and page breaks.
- [Merged and nested tables](08_tables.md): Combine table sections, row/column spans, cell backgrounds, width, borders, and nesting.
- [List numbering and nesting](09_lists.md): Use start values, li values, independent restarts, and nested numbered/bulleted lists.
- [Inline base64 images](10_data_images.md): Place data URL images inside a paragraph and set their display width.
- [Local images](11_local_images.md): Read files below an explicit base directory; paths outside it are refused.
- [Asset loaders and direct images](12_asset_loader.md): Resolve logical asset IDs to bytes and insert BytesIO images into cells.
- [MathML equations](13_mathml.md): Create editable fractions, scripts, indexed roots, delimiters, matrices, and inline equations.
- [LaTeX equations](14_latex.md): Use the optional frontend for sums, fractions, roots, and matrices.
- [Inline markers and block replacement](15_markers.md): Replace markers spanning formatted runs and insert multiple blocks into cells.
- [Bookmark replacement](16_bookmarks.md): Replace Word bookmark ranges while preserving surrounding content and bookmarks.
- [docxtpl integration](17_docxtpl.md): Render a Jinja template and then add HTML paragraphs.
- [Options and settings copies](18_options.md): Disable images, tables, math, or styles and independently copy settings.
- [Style helpers](19_style_helpers.md): Explicitly apply CSS text to a target run or paragraph.
- [Links and anchors](20_links.md): Use external/internal links, id/name anchors, and links without href.
- [Combined report](21_report.md): Combine stylesheets, images, merged tables, nested lists, equations, and page breaks.
- [Markdown integration](22_markdown.md): Convert headings, tables, lists, code, and strikethrough with the optional frontend.
- [Complex equation gallery](23_complex_equations.md): Compare 20 authored MathML and 24 LaTeX examples covering nested fractions, matrices, calculus, accents, and math alphabets.
- [Equation-heavy mixed report](24_dense_report.md): Combine 120 equation placements with merged/nested tables, lists, images, links, multilingual text, and page breaks.
- [Advanced research report](25_research_report.md): Ten distinct advanced MathML formulas with Korean/English prose, merged and nested tables, lists, images, links, and page breaks.
- [Advanced template workbook](26_template_workbook.md): Put the same advanced formulas into existing documents and table cells; combine marker replacement, nested tables, headers, footers, and a landscape page.
- [Advanced LaTeX report](27_advanced_latex.md): Eight distinct advanced LaTeX inputs exercise adjacent matrices, grouped powers, piecewise expressions, nested radicals, sums, and derivatives inside a formatted report.
