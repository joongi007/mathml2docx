#!/usr/bin/env bash
# Test the real legacy interpreter without altering the checkout or host Python.
set -euo pipefail
project_root="$(cd "$(dirname "$0")/.." && pwd)"
legacy_image="${1:-python:3.6.15-slim-buster}"
legacy_cache="${TMPDIR:-/tmp}/mathml2docx-legacy-pip-cache"
mkdir -p "$legacy_cache"
docker run --rm \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$project_root:/source:ro" \
  -v "$legacy_cache:/root/.cache/pip" \
  "$legacy_image" sh -eu -c '
    mkdir /tmp/project
    cp -R /source/mathml2docx /source/tests /source/examples /source/docs \
      /source/scripts /source/docs_site /source/.github /source/pyproject.toml \
      /source/README.md /source/README.ko.md /source/CHANGELOG.md /source/LICENSE /source/THIRD_PARTY_NOTICES.md /source/uv.lock \
      /source/.python-version /tmp/project/
    cd /tmp/project
    python -m pip install --disable-pip-version-check --upgrade "pip>=21.3,<22"
    python -m pip install --disable-pip-version-check ".[latex,markdown,test]"
    python -m unittest discover -v
    python -m pytest -q tests/test_math_audit_regressions.py tests/test_math_html_regressions.py
    python -c "import doctest; from mathml2docx import utils; result=doctest.testmod(utils); assert result.failed == 0 and result.attempted == 11"
    python -m pip wheel --no-deps . --wheel-dir /tmp/distributions
    python -m venv /tmp/wheel-env
    /tmp/wheel-env/bin/python -m pip install --disable-pip-version-check --upgrade "pip>=21.3,<22"
    /tmp/wheel-env/bin/python -m pip install --disable-pip-version-check "/tmp/distributions/$(ls /tmp/distributions | head -1)[latex,markdown]"
    cd /tmp
    /tmp/wheel-env/bin/python /tmp/project/scripts/smoke_distribution.py
  '
