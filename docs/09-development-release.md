# Development, compatibility, and publishing

## Preserved versions

The existing master history is not reset or force-pushed. These tags preserve
previous source states locally and remotely:

| Tag | Commit | Contents |
| --- | --- | --- |
| `v0.1.3-legacy` | `89205f4` | Original 0.1.3 source |
| `snapshot/pre-python36-compat` | `a8ef2ec` | 1.0 candidate before restoring Python 3.6 support |

Compatibility and validation work was reviewed on `compat/python36-uv` and merged
to master. These historical tags may still contain the old XSL; preservation does
not resolve its redistribution rights. See [provenance](06-xsl-provenance.md).

Publishing a GitHub Release is separate from merging or pushing source.
Ordinary pushes and tag creation do not upload packages.

## Development environment

Library users do not need uv. The core supports Python 3.6+, while development and
documentation use the recent Python in `.python-version`.

```sh
uv sync --locked --extra latex --extra markdown --extra test --group docs --group examples
uv run --no-sync python -m pytest -q
uv run --no-sync python -m unittest tests.test_docx_oracles -v
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/build_docs.py
uv build
uv run --no-sync python scripts/check_dist.py
uv run --no-sync twine check dist/*
uv run --no-sync python scripts/check_wheel_install.py
```

Use uv 0.13.7+. `pyproject.toml` is the dependency source of truth; `uv.lock` records
interpreter-specific resolution. Run `uv lock` after dependency/version changes.
There is no duplicate requirements.txt configuration.

- `[project.dependencies]`: runtime requirements.
- `[project.optional-dependencies]`: LaTeX, Markdown, and test extras.
- `[dependency-groups]`: development, docs, and example tools, not forced on users.
- `[tool.uv.dependency-groups]`: tool groups require Python 3.10+.

Release metadata tooling uses Python 3.11+; the workflow explicitly runs it on 3.14.
Its tests are skipped on older runtime interpreters without excluding conversion tests.

## Python 3.6 compatibility

Dependency ranges permit compatible historical releases. Python 3.6 selects
python-docx 0.8.11 and older CSS/LaTeX dependencies; recent Python can use newer ones.
HTML/MathML supports Python 3.6.0+. Optional LaTeX requires Python 3.6.2+ and
latex2mathml 3.64+. An early 3.6.0/3.6.1 LaTeX request reports that requirement.

The build backend is `flit_core>=3.11,<4`. Its 3.12 series supports Python 3.6/3.7
and the current metadata/license fields, so both wheel and source installs work.
Older python-docx omits hyperlink text from `paragraph.text`, but the saved XML
still contains the link and text; tests inspect XML and reopen documents.

```sh
bash scripts/test_legacy.sh
bash scripts/test_legacy.sh python:3.7.17-slim-bullseye
```

These Docker checks copy source into a temporary directory, install it, run all
runtime tests and 11 utility doctests, build a wheel, and install that wheel into a
clean venv. A smoke check runs outside the checkout and exercises CSS, templates,
equations, Markdown, saving, and reopening. Legacy pip is `>=21.3,<22`.

```sh
uv sync --locked --no-default-groups --python 3.8 --extra latex --extra markdown --extra test
uv run --no-sync --no-default-groups --python 3.8 python -m unittest discover -v
```

Use a separate environment or `--python` when switching versions: the default
development interpreter is 3.14. CI covers each minor from 3.6 to 3.14; 3.6/3.7 use
Docker and modern versions use uv. Windows 3.8/3.14 and macOS 3.14 are also checked.
uv support for an old interpreter does not imply it can download a Python 3.6
binary; the legacy check uses an explicit container image.

## CI and CD rules

| Event | Checks/build | Upload |
| --- | --- | --- |
| PR targeting master | Runtime tests, quality, docs | None |
| Push/merge to master | Runtime tests, quality, docs; Pages deployment attempted | No package upload |
| Tag push only | No release publishing event | None |
| Publish a candidate GitHub Release, e.g. `v1.0.0rc1`, marked prerelease | Full checks, version/source gates, distribution checks, clean wheel install | TestPyPI through `testpypi` environment |
| Publish stable GitHub Release, e.g. `v1.0.0` | Same gates | PyPI through `pypi` environment |
| Manual `Publish to PyPI` workflow run | Checks and build | None |

`check_release.py` requires the tag, pyproject version, module `__version__`, and
GitHub prerelease flag to agree. Release source must be an ancestor of
`origin/master`. An RC cannot be published as a stable release by only changing
the GitHub checkbox. A stable version cannot be used as an RC either.

The publish build checks wheel/sdist contents and metadata, runs Twine checks,
and installs the actual wheel in a fresh environment for API smoke tests. Upload
jobs only receive the validated artifact and OIDC permission, not a source checkout.
TestPyPI and PyPI are separate indexes, not automatic promotions of one another.

## First-time Trusted Publisher setup

Repository files do not configure your PyPI accounts or GitHub approval rules.
Configure both existing projects if you intend to use both indexes.

1. On PyPI, open `mathml2docx` → **Manage → Publishing → Add a new publisher**.
2. Register these GitHub publisher fields:

| Index | Owner | Repository | Workflow filename | Environment |
| --- | --- | --- | --- | --- |
| PyPI | `joongi007` | `mathml2docx` | `publish.yml` | `pypi` |
| TestPyPI | `joongi007` | `mathml2docx` | `publish.yml` | `testpypi` |

3. Repeat on TestPyPI using its separate account/project. Confirm project ownership;
   an existing project name alone does not establish publishing rights.
4. In GitHub **Settings → Environments**, configure `pypi` and `testpypi`.
5. Add **Required reviewers** and restrict deployment tags. If you trigger and
   approve your own personal-project releases, do not enable **Prevent self-review**.
6. Verify protection rules before publishing. Merely naming an environment in YAML
   does not create approval requirements.

Trusted Publishing uses `id-token: write`; no long-lived PyPI API key or password
is needed in GitHub Secrets. References: [publisher registration](https://docs.pypi.org/trusted-publishers/adding-a-publisher/),
[OIDC publishing and TestPyPI](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## Prepare a candidate and stable release

1. Complete direct Word inspection and review [migration](05-migration.md),
   [validation](11-validation.md), licensing, and the changelog.
2. For a candidate, set both package versions to `1.0.0rc1`, update `uv.lock`, and
   merge the tested commit to master. Create its `v1.0.0rc1` GitHub Release with
   **Set as a pre-release** enabled.
3. Passing checks allow the TestPyPI upload, subject to configured environment
   approval. Verify the exact candidate version installs and works from TestPyPI.
4. For stable, set both versions to `1.0.0`, update the lock and changelog, and merge
   the tested source. Publish `v1.0.0` as a stable GitHub Release and approve PyPI.
5. Correct a bad uploaded version with a new version; do not plan to overwrite it.

A manual workflow run can validate/build before any release is published. It does
not exercise the upload or prove account configuration is correct.
Pages is independent: enable **Settings → Pages → Source: GitHub Actions** to
publish documentation. It is not required for a PyPI package upload.

## Release readiness

Code-level preparation includes tests, independent DOCX answers, schema checks,
version/event gates, artifact checks, and an installed-wheel smoke check.
Before the first actual upload, still confirm:

- Direct Word display, editing, and resaving, including the known M17/M19/M20 differences.
- Ownership and Trusted Publishers for the desired indexes.
- Required reviewers and deployment restrictions on the GitHub environments.
- A successful candidate installation from TestPyPI after an intentional upload.
- Final version/changelog review and a plan for historical XSL-containing copies.
- Optionally, Pages activation for documentation/download hosting.

As checked on 2026-11-11, public PyPI reported 0.1.3 and TestPyPI 0.1.10; neither
contained 1.0.0. This observation does not verify your account permissions.
This maintenance work does not publish a Release, upload a package, change account
settings, or delete historical copies.

## Validation history

On 2026-11-10, the 108-test suite passed on Python 3.6 with both the default and
2.16.5 LaTeX backends, as did doctests and installation smoke checks. Those checks
were primarily structural/persistence checks and did not establish all equation meanings.
Python 3.7/3.8 were also exercised; Python 3.14 reported 108 tests plus 860 subcases.

Independent saved-DOCX answers added on 2026-11-11 exposed text/accent/spacing
mismatches in 2.16, which is no longer supported. The expanded runtime suite
reported 117 tests and 941 subcases on Python 3.14 before adding separate release-gate
tests, and passed on real Python 3.6.15 and Python 3.8. Input text and JSON answers
are retained; generated DOCX files are excluded from Git and source distributions.
See [validation scope](11-validation.md) for distinctions from direct Word checks.
