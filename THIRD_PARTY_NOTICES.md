# Third-party notices

This file records provenance and direct dependency licenses for mathml2docx.
It is an attribution inventory, not a replacement for any upstream license.

## Project code and inherited source

mathml2docx is derived from [pqzx/html2docx](https://github.com/pqzx/html2docx).
The upstream MIT copyright and permission notice are retained in [LICENSE](LICENSE):

- Copyright (c) 2019 pqzx
- Copyright (c) 2024-2026 joongi007

The project license covers project-authored code, documentation and newly authored
examples/assets. It does not relicense dependency packages, user documents or fonts.
Legacy test fixtures were inherited with the upstream source. Newly authored example
assets include `examples/assets/swatch.png` and `examples/assets/report.html`.

## Runtime dependencies

The following are direct dependencies, installed separately by the package manager;
the mathml2docx wheel does not vendor their source or binary distributions.
License labels were checked against the installed distribution notices or upstream
license files on 2026-11-10. Selected versions vary with the Python interpreter;
consult the exact installed package's notices when redistributing an environment.

| Package | Project-level license | Upstream |
| --- | --- | --- |
| python-docx | MIT | [License](https://github.com/python-openxml/python-docx/blob/master/LICENSE) |
| beautifulsoup4 | MIT | [Project](https://www.crummy.com/software/BeautifulSoup/) |
| lxml | BSD-3-Clause, with component-specific notices | [License inventory](https://github.com/lxml/lxml/blob/master/LICENSES.txt) |
| tinycss2 | BSD-3-Clause | [License](https://github.com/Kozea/tinycss2/blob/main/LICENSE) |
| Pillow | MIT-CMU, with bundled component notices | [License](https://github.com/python-pillow/Pillow/blob/main/LICENSE) |
| cssselect2 | BSD-3-Clause | [License](https://github.com/Kozea/cssselect2/blob/main/LICENSE) |

lxml and Pillow distributions can contain additional upstream libraries/resources
with their own notices. Their project-level license labels do not replace those
component-specific terms. Retain the notices shipped with the exact distributions
if bundling or redistributing those dependencies.

## Optional dependencies and tooling

| Package | Use | License / notice |
| --- | --- | --- |
| latex2mathml | Optional LaTeX frontend | [MIT](https://github.com/roniemartinez/latex2mathml/blob/master/LICENSE) |
| Python-Markdown | Optional Markdown frontend | [BSD-3-Clause](https://github.com/Python-Markdown/markdown/blob/master/LICENSE.md) |
| setuptools | Legacy LaTeX backend compatibility on Python 3.6.0/3.6.1 | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) |
| docxtpl | Optional tests/examples and user-selected integration | [Project](https://github.com/elapouya/python-docx-template), LGPL-2.1-only in tested 0.20.2 metadata |
| MkDocs | Documentation generation | [BSD-2-Clause](https://github.com/mkdocs/mkdocs/blob/master/LICENSE) |
| pytest | Test execution | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) |
| Ruff | Development lint/format | [MIT](https://github.com/astral-sh/ruff/blob/main/LICENSE) |
| flit_core | Build backend | [BSD-3-Clause](https://github.com/pypa/flit/blob/main/LICENSE) |

Development, documentation and example dependency groups are not mandatory runtime
requirements. This table is not an exhaustive inventory of every transitive package;
`uv.lock` records the resolved versions, and each distribution supplies its own terms.

The independent validation scripts can download ECMA-376 and W3C XML schemas into
an explicitly selected external directory. Those schemas retain their original
terms and are not included in this repository's source or binary distributions.
They are validation inputs, not conversion templates or runtime dependencies.

## XSL removal

Older source revisions included `mathml2docx/MML2OMML.XSL` without a recorded grant
of redistribution rights. That stylesheet is absent from the 1.0.0 source tree,
wheel and source distribution. The native converter in `mathml2docx/math.py` builds
OMML elements directly and does not execute or load an Office stylesheet. The
stylesheet code and templates were not copied into the native converter.

Removing the stylesheet from new distributions does not establish permission for,
or alter, historical copies in Git history, preservation tags or old PyPI releases.
See [the provenance record](https://github.com/joongi007/mathml2docx/blob/master/docs/06-xsl-provenance.md) for the hash and evidence.

## Generated previews and fonts

Reference PDFs are generated from the project-authored examples with LibreOffice;
LibreOffice itself and original font files are not bundled in this package.
PDF font subsets retain the embedding information produced by the renderer. Font
licenses and availability are separate from this project's MIT license. The preview
rendering environment used Noto CJK, Liberation and DejaVu fonts as available.
