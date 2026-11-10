"""Build the documentation and package its agent-facing downloads."""

import json
import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    # Create linked assets before strict link validation runs.
    assets = ROOT / "docs" / "downloads"
    assets.mkdir(exist_ok=True)
    skill = ROOT / "skills" / "mathml2docx"
    with ZipFile(assets / "mathml2docx-skill.zip", "w", ZIP_DEFLATED) as archive:
        for path in sorted(skill.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(skill.parent))

        archive.write(ROOT / "LICENSE", "mathml2docx/LICENSE")
        archive.write(
            ROOT / "THIRD_PARTY_NOTICES.md", "mathml2docx/THIRD_PARTY_NOTICES.md"
        )

    catalog = json.loads((ROOT / "examples/catalog.json").read_text(encoding="utf-8"))
    output = assets / "examples"
    env = dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=str(output))
    subprocess.run(
        [sys.executable, "-m", "examples.run_all"],
        cwd=ROOT,
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    gallery = ROOT / "docs/examples"
    gallery.mkdir(exist_ok=True)
    overview = [
        "# Runnable examples",
        "",
        f"The documentation build executes {len(catalog)} Python examples to generate DOCX downloads.",
        "",
        "```sh",
        "uv sync --locked --extra latex --extra markdown --group docs --group examples",
        "uv run --no-sync python -m examples.run_all",
        "```",
        "",
        "Run from a repository checkout after installing the dependencies above. Local outputs go to `examples/output/`. Run an individual example with, for instance, `python -m examples.01_quickstart`.",
        "",
        "[All example source and assets (ZIP)](../downloads/mathml2docx-examples.zip)",
        "",
        "The reference PDFs were rendered with LibreOffice 7.3.7. They are historical previews, not automatically refreshed by this build; Word versions and fonts may produce different results.",
        "",
    ]
    for stem, (title, description) in catalog.items():
        source = (ROOT / "examples" / (stem + ".py")).read_text(encoding="utf-8")
        content = [
            "# " + title,
            "",
            description,
            "",
            "## Run",
            "",
            "```sh",
            "python -m examples." + stem,
            "```",
            "",
            "[Generated DOCX](../downloads/examples/" + stem + ".docx)",
            "",
        ]
        pdf = ROOT / "docs/assets/previews" / (stem + ".pdf")
        if pdf.is_file():
            content.extend(["[Reference PDF](../assets/previews/" + stem + ".pdf)", ""])
        content.extend(
            ["## Complete source", "", "```python", source.rstrip(), "```", ""]
        )
        if stem == "21_report":
            content.extend(
                [
                    "## Input HTML",
                    "",
                    "```html",
                    (ROOT / "examples/assets/report.html").read_text(encoding="utf-8"),
                    "```",
                    "",
                ]
            )
        if stem == "23_complex_equations":
            content.extend(
                [
                    "## Visual comparison notes",
                    "",
                    "In the LibreOffice 7.3 reference PDF, M17 phantom width, M19 bevelled fractions, and M20 string quotes differ from the intended display. Their structures, properties, and characters are retained in XML, but visual equivalence has not been established. Direct Microsoft Word checks also remain outstanding.",
                    "",
                    "[Validation scope and limitations](../11-validation.md)",
                    "",
                ]
            )
        (gallery / (stem + ".md")).write_text("\n".join(content), encoding="utf-8")
        overview.extend(["- [" + title + "](" + stem + ".md): " + description])
    (gallery / "00-index.md").write_text("\n".join(overview) + "\n", encoding="utf-8")
    with ZipFile(assets / "mathml2docx-examples.zip", "w", ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / "examples").rglob("*")):
            if (
                path.is_file()
                and "output" not in path.parts
                and "__pycache__" not in path.parts
            ):
                archive.write(path, path.relative_to(ROOT))
        archive.write(ROOT / "LICENSE", "LICENSE")
        archive.write(ROOT / "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md")

    pages = [ROOT / "docs" / "index.md"] + sorted(
        (ROOT / "docs").glob("[0-9][0-9]-*.md")
    )
    pages += sorted(gallery.glob("*.md"))
    index = [
        "# mathml2docx",
        "",
        "> HTML and MathML to Word documentation.",
        "",
        "## Docs",
        "",
    ]
    full = []
    for path in pages:
        content = path.read_text(encoding="utf-8")
        title = content.splitlines()[0].removeprefix("# ")
        suffix = (
            ""
            if path.stem == "index"
            else str(path.relative_to(ROOT / "docs").with_suffix("")) + "/"
        )
        url = "https://joongi007.github.io/mathml2docx/" + suffix
        index.append(f"- [{title}]({url})")
        full.append(f"Source: {url}\n\n{content}")
    (ROOT / "docs" / "llms.txt").write_text("\n".join(index) + "\n", encoding="utf-8")
    (ROOT / "docs" / "llms-full.txt").write_text(
        "\n\n---\n\n".join(full), encoding="utf-8"
    )
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict"], cwd=ROOT, check=True
    )


if __name__ == "__main__":
    main()
