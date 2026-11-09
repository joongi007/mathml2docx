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
        "# 실행 예제 모음",
        "",
        f"Python 실행 예제 {len(catalog)}개를 문서 빌드에서 실제 실행해 DOCX로 만듭니다.",
        "",
        "```sh",
        "uv sync --locked --extra latex --extra markdown --group docs --group examples",
        "uv run --no-sync python -m examples.run_all",
        "```",
        "",
        "저장소를 내려받고 위 설치 명령을 실행한 환경에서 사용합니다. 모든 결과는 `examples/output/`에 저장됩니다. 개별 실행은 `python -m examples.01_quickstart`처럼 합니다.",
        "",
        "[전체 예제 코드·자산 ZIP](../downloads/mathml2docx-examples.zip)",
        "",
        "아래 PDF는 LibreOffice 7.3.7로 렌더링한 참조 결과입니다. Word 버전·글꼴에 따라 화면은 달라질 수 있습니다.",
        "",
    ]
    for stem, (title, description) in catalog.items():
        source = (ROOT / "examples" / (stem + ".py")).read_text(encoding="utf-8")
        content = [
            "# " + title,
            "",
            description,
            "",
            "## 실행",
            "",
            "```sh",
            "python -m examples." + stem,
            "```",
            "",
            "[생성 DOCX](../downloads/examples/" + stem + ".docx)",
            "",
        ]
        pdf = ROOT / "docs/assets/previews" / (stem + ".pdf")
        if pdf.is_file():
            content.extend(["[PDF 참조 결과](../assets/previews/" + stem + ".pdf)", ""])
        content.extend(["## 전체 코드", "", "```python", source.rstrip(), "```", ""])
        if stem == "21_report":
            content.extend(
                [
                    "## 입력 HTML",
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
                    "## 화면 비교 시 확인할 점",
                    "",
                    "LibreOffice 7.3 참조 PDF에서 M17 phantom 예약 폭, M19 bevelled 분수, M20 문자열 따옴표는 기대와 다르게 표시됩니다. XML에는 해당 구조·속성·문자가 남아 있지만 화면 동등성 검증을 완료한 항목은 아닙니다. Microsoft Word 직접 확인도 남아 있습니다.",
                    "",
                    "[전체 검증 범위와 한계](../11-validation.md)",
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
