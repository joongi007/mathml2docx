"""Require a successful TestPyPI publish/install workflow for this exact commit."""

import argparse
import json
import os
import re
import subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def verified_run(runs, sha, repository):
    for run in runs:
        if (
            run.get("head_sha") == sha
            and run.get("head_branch") == "master"
            and run.get("event") in ("push", "workflow_dispatch")
            and run.get("status") == "completed"
            and run.get("conclusion") == "success"
            and run.get("path") == ".github/workflows/testpypi.yml"
            and run.get("head_repository", {}).get("full_name") == repository
        ):
            return run
    raise ValueError(
        "No successful TestPyPI upload and installation check for commit " + sha
    )


def require_testpypi(sha, repository, token=None):
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository
    ):
        raise ValueError("Expected a full commit SHA and owner/repository")
    query = urlencode(
        {"head_sha": sha, "branch": "master", "status": "completed", "per_page": 100}
    )
    request = Request(
        f"https://api.github.com/repos/{repository}/actions/workflows/testpypi.yml/runs?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mathml2docx-release",
        },
    )
    if token:
        request.add_header("Authorization", "Bearer " + token)
    with urlopen(request, timeout=30) as response:
        runs = json.load(response)["workflow_runs"]
    return verified_run(runs, sha, repository)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "joongi007/mathml2docx"),
    )
    args = parser.parse_args()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    run = require_testpypi(sha, args.repository, os.environ.get("GH_TOKEN"))
    print("Verified TestPyPI workflow:", run["html_url"])


if __name__ == "__main__":
    main()
