# Runnable examples

Explore 30 complete examples. Download a Word document or run its Python source locally.

[All example source and assets (ZIP)](../downloads/mathml2docx-examples.zip)

Download and extract the ZIP, then run the following commands from the folder containing `examples/`. The bundle includes helper modules and assets used by the examples.

Running all examples requires Python 3.6.2+ for LaTeX. Example 17 also uses docxtpl, included in the installation command below.

```sh
python -m pip install "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
python -m examples.run_all
```

Outputs go to `examples/output/`. To run one example, use `python -m examples.01_quickstart`. The commands use the published PyPI package.

In an initialized uv or Poetry project, use the corresponding commands below instead. See [installation](../01-getting-started.md) for project setup. For a single example, replace `examples.run_all` with its module name.

```sh
uv add "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
uv run python -m examples.run_all
```

```sh
poetry add "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
poetry run python -m examples.run_all
```

Open an example to compare its HTML/MathML in the browser with the LibreOffice PDF output. Use the DOCX download to edit equations in Word. Fonts and document applications can change line wrapping and pagination.

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
- [Chemical notation and enclosures](28_chemistry_enclosures.md): Upright element symbols, isotope prescripts, charges, reaction arrows and native enclosures.
- [MathML recovery and image fallbacks](29_math_fallbacks.md): Preserve unsupported source or embed an explicitly supplied rendered expression.
- [MathML notation and document fidelity](30_mathml_fidelity.md): Inherited defaults, inline/display sums, composite scripts, equation-safe templates, cell layout, CSS and Unicode.
