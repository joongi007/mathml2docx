# Documentation deployment

## Local build

Run from the repository root with Python 3.10+:

```sh
uv sync --locked --extra latex --extra markdown --group docs --group examples
uv run --no-sync python scripts/build_docs.py
python -m http.server 8000 --directory site
```

Open `http://localhost:8000` for English or `http://localhost:8000/ko/` for Korean.
The language selector opens the equivalent page in the other language. Each locale
has its own navigation, search index, `llms.txt`, and `llms-full.txt`. Both provide
skill and example downloads, sharing the same executable sources and binary originals.

Both builds use MkDocs `--strict`, so documentation warnings fail the build.
Post-build checks verify the paired pages (currently 38 per language), actual HTML
language, equivalent-page links, search indexes, and downloads. Adding translated
pages automatically extends the checked page set.

## GitHub Pages

Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
After a change reaches `master`, the `Documentation` workflow builds both languages
as one site and deploys through the `github-pages` environment. Pull requests only
build the site. The workflow can also be started manually in Actions.

English uses `https://joongi007.github.io/mathml2docx/`; Korean uses
`https://joongi007.github.io/mathml2docx/ko/`.
Adding a workflow does not itself enable the site. Check the repository's Pages
settings and the deployment result.

## Content and translation sources

| Content | English | Korean |
| --- | --- | --- |
| README | `README.md` | `README.ko.md` |
| Guides | `docs/*.md` | `docs/ko/*.md` |
| Navigation/search configuration | `mkdocs.yml` | `mkdocs.ko.yml` |
| Example descriptions | `examples/catalog.json` | `examples/catalog.ko.json` |
| Generated example pages | `docs/examples/` | `docs/ko/examples/` |

Update both languages with API changes and add new pages to both navigation menus.
Edit example descriptions in the catalogs; direct changes to generated pages are
overwritten on the next build. Example code lives in `examples/`, and the agent
skill source is `skills/mathml2docx/`. The skill is in English; machine-readable
documentation is generated from each locale's own text.

Do not commit `site/`, generated DOCX files, or the build copies under
`docs/ko/assets/` and `docs/ko/downloads/`. Reference PDF originals are stored once
under `docs/assets/previews/`. Regenerate with `python scripts/render_examples.py`
and copy reviewed PDFs there; this requires a separate LibreOffice installation.
Existing PDFs are historical previews, not automatically refreshed by docs builds.

## Is MkDocs required?

No. GitHub Pages hosts static HTML, CSS, and JavaScript, including custom sites.
This project currently retains MkDocs to use its navigation, search, link checks,
and theme while keeping Markdown sources and existing URLs. Two configurations
build the locales; a small shared template and hook add language switching without
a separate localization plugin.

A dedicated layout or interactive converter could use theme extensions or a custom
site. Markdown, example catalogs, and Python examples are independent of the site
engine. Preserve existing URLs, language pairing, search, downloads, and
accessibility when migrating.

References: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [MkDocs theme customization](https://www.mkdocs.org/user-guide/customizing-your-theme/).
