"""Validate release metadata with the development Python (3.11+)."""

import argparse
import ast
import subprocess
from pathlib import Path


def release_version(root, tag=None, prerelease=False):
    import tomllib
    from packaging.version import Version

    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    module = ast.parse((root / "mathml2docx/__init__.py").read_text(encoding="utf-8"))
    versions = [
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(name, ast.Name) and name.id == "__version__"
            for name in node.targets
        )
    ]
    if versions != [project["version"]]:
        raise ValueError("Package __version__ and pyproject version must match")
    version = Version(project["version"])
    if tag is not None:
        if tag != "v" + project["version"]:
            raise ValueError(
                "Release tag must match package version: v" + project["version"]
            )
        if prerelease != (version.is_prerelease or version.is_devrelease):
            raise ValueError("GitHub prerelease status must match the package version")
    return str(version)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    parser.add_argument("--prerelease", choices=["true", "false"], default="false")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = release_version(root, args.tag, args.prerelease == "true")
    if args.tag:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", "origin/master"],
            cwd=root,
            check=True,
        )
    print("Release metadata validated:", version)


if __name__ == "__main__":
    main()
