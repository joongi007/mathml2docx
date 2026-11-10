# Choosing a tool

Editable Word equations alone do not make this project a unique option. The
following feature descriptions were checked against official documentation on
2026-11-10. They are not a same-input benchmark or a ranking of fidelity or performance.

| Tool | Documented functionality | Considerations |
| --- | --- | --- |
| [Pandoc](https://pandoc.org/MANUAL.html#math) | Multiple document formats and DOCX equations in OMML | Consider it for whole-document Markdown/LaTeX conversion pipelines. |
| [html4docx](https://github.com/dfop02/html4docx) | HTML-to-DOCX with CSS, image, table, and list improvements | A Python alternative descended from the same upstream; compare actual inputs and API compatibility. |
| [Microsoft 365](https://learn.microsoft.com/en-us/office/math/mathml) | MathML import/export and OMML storage | Consider Word's built-in equation features when working directly in Word. |
| mathml2docx | Python API, supported MathML inside HTML, optional LaTeX, existing document/cell/marker/bookmark insertion | Useful for integration into an existing python-docx workflow on a server or locally. |

The goal is to make HTML/equation insertion into existing Word documents concise
in Python, while publishing support boundaries and reproducible checks. Conversion
can run without an external upload. Whether explicitly supplied image/CSS loaders
access the network is controlled by the calling application.

The project's practical value depends on how much work it saves for its users.
Implementation and tests alone do not establish demand or superior fidelity over
other tools. Collect real reports, teaching materials, and question papers after
release, then extend the [validation corpus](11-validation.md) from that feedback.
