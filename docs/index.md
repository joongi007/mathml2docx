# mathml2docx

A Python library for converting HTML and MathML equations into Word documents (`.docx`).
MathML is converted directly to editable OMML equations without XSL or an Office installation.
Optional frontends accept LaTeX and Markdown.

- [Getting started](01-getting-started.md): installation, files, and existing documents
- [API and options](02-api.md): methods, styles, image loading, and conversion limits
- [Recipes](08-recipes.md) and [24 runnable examples](examples/00-index.md)
- [Input files and independent DOCX checks](11-validation.md)
- [Development, compatibility, and PyPI publishing](09-development-release.md)
- [Documentation deployment](04-publishing.md)
- [Migrating to 1.0.0](05-migration.md)
- [Review of 49 upstream issues](07-upstream-audit.md)
- [XSL provenance investigation](06-xsl-provenance.md) and [licensing scope](10-licensing.md)
- [Choosing a tool](12-choosing.md)

This project is derived from [html2docx](https://github.com/pqzx/html2docx).
It does not reproduce an entire browser rendering engine. Check your actual
HTML, equations, and formatting against the generated document.
