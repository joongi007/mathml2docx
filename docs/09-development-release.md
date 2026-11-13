# Development and releases

## Development environment

For package installation and usage, start with [getting started](01-getting-started.md).
This section is for contributors working on the source. The core supports Python
3.6+, while development and documentation use the Python pinned in `.python-version`.

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
git switch develop
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

The documentation build runs the examples and records their HTML/MathML inputs
for sandboxed browser previews. Existing-document examples show input fragments,
not a reconstruction of their Word templates. Reference PDFs are exported with
LibreOffice; regenerate them with the [validation tools](11-validation.md) after
changing an example's output. The docs-only pypdfium2 dependency renders every
PDF page for browsers without an embedded PDF viewer. Generated preview HTML,
page images and DOCX are build artifacts.

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
Docker and modern versions use uv. Windows 3.8/3.14 and macOS 15 Arm64 with Python
3.14 are also checked.
uv support for an old interpreter does not imply it can download a Python 3.6
binary; the legacy check uses an explicit container image.

## Branch workflow

`master` is the release branch. Start everyday work from `develop`:

```sh
git switch develop
git pull --ff-only
git switch -c feature/table-layout
# Commit, test, and open a PR targeting develop.
```

Use a branch such as `release/1.0.2` from develop for stabilization if useful. Merge the release
branch into master when ready to exercise TestPyPI, and bring final fixes back to
develop. A release branch is optional for a small release; develop can target
master directly. No packages are uploaded by develop/feature PRs or pushes.

| Event | Checks/build | Upload |
| --- | --- | --- |
| Push to develop; PR targeting develop/master | Python 3.6–3.14, quality, docs, packaging checks | None |
| Push/merge to master | Same full suite, unique candidate build, clean wheel check | TestPyPI; then installation checks from that index |
| Push a final tag `vX.Y.Z` on a verified master commit | Version/source gate, exact-commit TestPyPI success, full tests, final distribution/install checks | PyPI through `pypi` |
| Publish GitHub Release notes for an existing tag | No additional package upload | None |
| Manual `TestPyPI candidate` on master | Same candidate pipeline | TestPyPI and installation checks |
| Manual `Publish to PyPI` | Checks and build | None |

Master's package checks run inside `TestPyPI candidate` using the reusable Python
workflow. They are not launched a second time as a standalone push workflow.
The separate Documentation workflow builds both locales and deploys only master.

## Automatic TestPyPI installation check

Master stores the intended final version, for example `1.0.0`. The temporary CI
checkout receives `1.0.0.dev<run_id><attempt padded to 3 digits>` in both version
fields and regenerates its lockfile. This does not commit a version bump.
Each run and full retry has a different candidate version, avoiding same-version
upload collisions. The workflow summary shows the exact published candidate.

After upload, Python 3.8 and 3.14 jobs obtain the version's actual TestPyPI JSON
metadata. They require the filename and SHA-256 to match the built wheel and
install its official TestPyPI download URL into a new venv. Dependencies come only
from PyPI; the two indexes are not mixed with `--extra-index-url`. The smoke check
runs outside the checkout and exercises CSS, MathML, LaTeX, Markdown, template
replacement, saving, and reopening. Python 3.6/3.7 source and wheel installation
are checked by the preceding Docker jobs.

A passed local-wheel check alone does not pass the TestPyPI workflow. Upload and
both remote installation jobs must succeed. A short retry handles index visibility
delay. A full rerun uses a new candidate version; after a partial upload failure,
choose **Re-run all jobs** rather than repeatedly uploading the existing version.

## First-time Trusted Publisher setup

Repository files do not configure account ownership, GitHub protection rules, or
Trusted Publishers. Configure both existing index projects:

| Index | Owner | Repository | Workflow filename | Environment |
| --- | --- | --- | --- | --- |
| TestPyPI | `joongi007` | `mathml2docx` | `testpypi.yml` | `testpypi` |
| PyPI | `joongi007` | `mathml2docx` | `publish.yml` | `pypi` |

1. Open each project's **Manage → Publishing → Add a new publisher** and register
   the row above. TestPyPI has its own account and project permissions.
2. Configure GitHub **Settings → Environments → testpypi / pypi**.
3. To automate master candidates without a pause, leave required reviewers off
   for `testpypi` and permit the master branch. Add required reviewers to `pypi`
   and permit final release tags. Naming an environment in YAML does not add
   approval rules. For a personal project, do not prevent self-review if you need
   to approve your own release.
4. Protect master and develop using PR reviews/required CI checks as desired;
   restrict creation/deletion of `v*` tags with a ruleset if needed.

Trusted Publishing uses OIDC `id-token: write`, not a long-lived API key in Secrets.
See [publisher registration](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
and [using a publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
Before this setup succeeds, candidate upload/install cannot be reported as verified.

## Create a final release tag

1. Complete Word inspection and review [migration](05-migration.md),
   [validation](11-validation.md), licensing, and the changelog.
   Check that README and user guides use the published package's pip installation
   commands, and update the release date and status before publication.
2. Set both package versions to the intended stable version, update `uv.lock`,
   test, and merge the source to master.
3. Wait for that exact master commit's **TestPyPI candidate** workflow to pass,
   including upload and both installation jobs. A successful run for another
   commit, a PR, develop, or only a local wheel does not qualify.
4. Tag that commit and push the tag:

For example, for a prepared `1.0.2` release (substitute the version in
`pyproject.toml`; existing release tags must remain unchanged):

```sh
git switch master
git pull --ff-only
# Confirm this HEAD's complete TestPyPI candidate run is green first.
git tag -a v1.0.2 -m 'Release 1.0.2'
git push origin v1.0.2
```

`Publish to PyPI` requires the tag to match pyproject and `__version__`, the tagged
commit to be included in origin/master, and a successful `testpypi.yml` workflow
for exactly that SHA in this repository. It repeats the full suite and checks the
final wheel before uploading, subject to environment approval. GitHub Release
notes can be created afterward without causing another upload.

The workflow blocks publication from unverified tags; it cannot prevent users
from creating a local Git tag. Repository tag rules govern who may push tags.
A tag created before TestPyPI succeeds fails the publish gate; rerun after the
verification completes. Use a new version to correct an already uploaded release.
TestPyPI candidates and final PyPI releases have different version metadata and
are rebuilt from the same source commit, not promoted as identical artifacts.

## Hotfixes

Keep master on the release line; unfinished features stay on develop/release
branches. Choose an unused patch version; the commands below use `1.0.2` as an
example. Branch a hotfix from the current master release line:

```sh
git switch master
git pull --ff-only
git switch -c hotfix/1.0.2
# Fix, add a regression case, and update both versions plus uv.lock to 1.0.2.
# Open a PR targeting master; merge after checks.
```

Wait for the merged master commit's TestPyPI upload and installation checks, then
tag `v1.0.2` on that commit. Merge master back into develop (or open a back-merge
PR) so the fix survives the next release. If develop already targets `1.1.0`,
resolve version/lock conflicts while keeping develop's intended version.
This flow keeps a hotfix independent of unreleased features.
