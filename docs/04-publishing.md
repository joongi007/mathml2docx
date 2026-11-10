# Documentation deployment

## Local build

Run from the repository root with Python 3.10+:

```sh
uv sync --locked --extra latex --extra markdown --group docs --group examples
uv run --no-sync python scripts/build_docs.py
python -m http.server 8000 --directory site
```

Open `http://localhost:8000`. The `site/` directory contains HTML, the search index,
`llms.txt`, `llms-full.txt`, and `downloads/mathml2docx-skill.zip`.
The build uses MkDocs `--strict`, so documentation warnings fail the build.

## GitHub Pages

Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
After a change reaches `master`, the `Documentation` workflow builds and deploys
through the `github-pages` environment. Pull requests only build the site.
The workflow can also be started manually in Actions.

The configured URL is `https://joongi007.github.io/mathml2docx/`.
Adding a workflow does not itself enable the site. Check the repository's Pages
settings and the deployment result.

Edit content under `docs/`, navigation in `mkdocs.yml`, and the agent skill under
`skills/mathml2docx/`. Add new pages to the navigation. Update examples with API
changes and do not commit generated site output or DOCX downloads.

References: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [MkDocs deployment](https://www.mkdocs.org/user-guide/deploying-your-docs/).

Edit example code together with `examples/catalog.json`. The build executes all
examples and generates `docs/examples/` pages with full source and download links.
Direct edits to generated descriptions are overwritten; edit the catalog instead.
Reference PDFs can be regenerated with `python scripts/render_examples.py` and
copied into `docs/assets/previews/`. This requires a separate LibreOffice installation.
