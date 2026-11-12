# Building the documentation

The documentation is a static HTML site rendered from Markdown by the project's
Python builder. It uses Jinja2 templates and Pygments for code highlighting;
MkDocs and a JavaScript build toolchain are not required.

## Build and preview locally

Run from a repository checkout with Python 3.10+ and uv 0.13.7+:

```sh
uv sync --locked --all-extras --group docs --group examples
uv run --no-sync python scripts/build_docs.py
python -m http.server 8000 --directory site
```

Open `http://localhost:8000/` for English and `http://localhost:8000/ko/` for Korean.
The build executes the Python examples, generates DOCX and source ZIP downloads,
then renders both languages. It checks local links, anchors, paired translations,
search indexes and downloads before replacing the output directory.
Use `--output PATH` to build into another generated directory.

## Edit content and layout

| Content | Source |
| --- | --- |
| English / Korean guides | `docs/*.md` / `docs/ko/*.md` |
| Navigation in both languages | `docs_site/navigation.json` |
| Page template, design tokens and behavior | `docs_site/page.html`, `site.css`, `site.js` |
| Example titles and descriptions | `examples/catalog.json`, `catalog.ko.json` |
| Executable example code | `examples/` |
| Markdown rendering and link validation | `scripts/site_builder.py` |

Add each page in both languages and list it in each navigation. Existing URLs are
preserved when replacing Markdown rendering or layout. Edit generated example
pages through the catalogs and Python sources; builds regenerate their Markdown.

Search runs in the browser against a local, language-specific JSON index.
It supports substring queries for English, Korean and API names. Search results
are inserted as text, not HTML. Content and navigation remain readable without
JavaScript; interactive search and copy buttons require JavaScript.

## Deployment

In GitHub, set **Settings → Pages → Build and deployment → Source** to
**GitHub Actions**. The `Documentation` workflow builds pull requests and develop
pushes; it deploys only master builds to the `github-pages` environment.

Do not commit the generated `site/`, DOCX files or example output folders.
To refresh reference PDFs, install LibreOffice Writer, Math, fonts and Poppler,
then use [the rendering checks](11-validation.md#libreoffice). PDF previews are
separate from editable DOCX downloads.
