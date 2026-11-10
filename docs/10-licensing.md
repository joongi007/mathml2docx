# Licensing and XSL replacement scope

## Project and dependencies

Project code is provided under the [MIT license](https://github.com/joongi007/mathml2docx/blob/master/LICENSE).
The upstream `Copyright (c) 2019 pqzx` notice is retained; this project's author
notice is `Copyright (c) 2024-2026 joongi007`.

This does not relicense dependencies as MIT. Runtime dependencies include MIT,
BSD-3-Clause, and MIT-CMU licenses; lxml and Pillow binary distributions carry
additional component notices. Optional docxtpl tests and integration are subject
to its LGPL terms. Check the notices for the actual versions and distribution forms.
[Third-party notices](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md)
record direct dependency provenance and investigation scope, and are included with
LICENSE in both wheel and source distributions.

## What replaced the XSL

The old `MML2OMML.XSL`, path/loading code, and XSLT call were removed. The converter
parses MathML XML and constructs OMML nodes for supported elements. Optional LaTeX
passes through latex2mathml and the same native converter. The old XSL templates
were not translated into Python or copied into the new implementation.

Regression tests block `etree.XSLT` and file-based `etree.parse` while converting
fractions, scripts, and radicals. Distribution checks enforce XSL exclusion and
inclusion of project and third-party license notices.

This does not mean the replacement reproduces every Office XSL feature or result.
See [math support](05-migration.md). Unsupported tags raise
`UnsupportedMathMLError`; not every presentation attribute on supported tags is reproduced.

## Unresolved historical questions

The old file matches a public AbiWord copy byte for byte. The actual source site
and permission to redistribute remain unconfirmed. Adding an MIT notice does not
create such permission. The [provenance record](06-xsl-provenance.md) preserves the
evidence and distinguishes it from conclusions that cannot be established.

Removing the XSL from new distributions does not change rights to historical Git
revisions, preservation tags, or existing PyPI packages. These notices document
what was checked; they do not certify every historical rights relationship.
