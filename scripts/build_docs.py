"""Build English/Korean documentation and runnable example downloads."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://joongi007.github.io/mathml2docx/"
COPY = {
    "en": {
        "overview": "Runnable examples",
        "intro": "Explore {count} complete examples. Download a Word document or run its Python source locally.",
        "run": "Run",
        "docx": "Generated DOCX",
        "pdf": "Reference PDF",
        "source": "Complete source",
        "input": "Input HTML",
        "zip": "All example source and assets (ZIP)",
        "local": "Run from a repository checkout after installing the dependencies above. Local outputs go to `examples/output/`. Run an individual example with, for instance, `python -m examples.01_quickstart`.",
        "previews": "PDF previews show the LibreOffice output. Use the DOCX download to edit equations in Word. Fonts and document applications can change line wrapping and pagination.",
        "notes": "Visual comparison notes",
        "limits": "Some equation properties vary between Word and LibreOffice, particularly phantom spacing, bevelled fractions and string quotes. Compare the input with the generated document when those details matter.",
        "validation": "Validation scope and limitations",
    },
    "ko": {
        "overview": "실행 예제",
        "intro": "완전한 예제 {count}개를 살펴보세요. Word 문서를 내려받거나 Python 코드를 직접 실행할 수 있습니다.",
        "run": "실행",
        "docx": "생성된 DOCX",
        "pdf": "참조 PDF",
        "source": "전체 코드",
        "input": "입력 HTML",
        "zip": "전체 예제 코드와 자산 (ZIP)",
        "local": "위 의존성을 설치한 뒤 저장소 루트에서 실행하세요. 로컬 결과는 `examples/output/`에 저장됩니다. 개별 예제는 `python -m examples.01_quickstart`처럼 실행할 수 있습니다. 실행 코드는 두 언어 문서가 공유합니다.",
        "previews": "PDF에서 LibreOffice 출력 결과를 살펴볼 수 있습니다. Word에서 수식을 편집하려면 DOCX를 내려받으세요. 글꼴과 문서 프로그램에 따라 줄바꿈·페이지 배치가 달라질 수 있습니다.",
        "notes": "화면 비교 시 참고할 점",
        "limits": "phantom의 예약 공간, 기울어진 분수, 문자열 따옴표 등은 Word와 LibreOffice에서 다르게 표시될 수 있습니다. 이런 세부 표현이 중요하면 입력과 생성된 문서를 함께 비교하세요.",
        "validation": "검증 범위와 한계",
    },
}


def example_pages(language, docs, catalog):
    text = COPY[language]
    gallery = docs / "examples"
    gallery.mkdir(exist_ok=True)
    overview = [
        "# " + text["overview"],
        "",
        text["intro"].format(count=len(catalog)),
        "",
        "```sh",
        "uv sync --locked --extra latex --extra markdown --group docs --group examples",
        "uv run --no-sync python -m examples.run_all",
        "```",
        "",
        text["local"],
        "",
        f"[{text['zip']}](../downloads/mathml2docx-examples.zip)",
        "",
        text["previews"],
        "",
    ]
    for stem, (title, description) in catalog.items():
        source = (ROOT / "examples" / (stem + ".py")).read_text(encoding="utf-8")
        content = [
            "# " + title,
            "",
            description,
            "",
            "## " + text["run"],
            "",
            "```sh",
            "python -m examples." + stem,
            "```",
            "",
            f"[{text['docx']}](../downloads/examples/{stem}.docx)",
            "",
        ]
        if (ROOT / "docs/assets/previews" / (stem + ".pdf")).is_file():
            content.extend([f"[{text['pdf']}](../assets/previews/{stem}.pdf)", ""])
        content.extend(
            ["## " + text["source"], "", "```python", source.rstrip(), "```", ""]
        )
        if stem == "21_report":
            content.extend(
                [
                    "## " + text["input"],
                    "",
                    "```html",
                    (ROOT / "examples/assets/report.html").read_text(encoding="utf-8"),
                    "```",
                    "",
                ]
            )
        if stem == "30_mathml_fidelity":
            notice = (
                "This DOCX targets Word. LibreOffice can misparse quoted `ms` strings, "
                "omit text or show a formula error in this PDF preview. For LibreOffice "
                "output, select `math_target='libreoffice'` and source/image recovery; "
                "native `ms` is rejected for that target."
                if language == "en"
                else "이 DOCX는 Word를 대상으로 합니다. LibreOffice가 따옴표가 있는 `ms` 문자열을 "
                "잘못 해석해 이 PDF에서 일부 글자를 생략하거나 수식 오류를 표시할 수 있습니다. "
                "LibreOffice용 출력에는 `math_target='libreoffice'`와 원문·이미지 대체 처리를 "
                "선택하세요. 해당 대상에서는 기본 `ms` 변환을 거절합니다."
            )
            content.extend(
                [
                    "## " + text["notes"],
                    "",
                    notice,
                    "",
                    f"[{text['validation']}](../11-validation.md)",
                    "",
                ]
            )
        if stem == "23_complex_equations":
            content.extend(
                [
                    "## " + text["notes"],
                    "",
                    text["limits"],
                    "",
                    f"[{text['validation']}](../11-validation.md)",
                    "",
                ]
            )
        if stem in {"25_research_report", "26_template_workbook", "27_advanced_latex"}:
            inputs = json.loads(
                (ROOT / "examples/assets/advanced-math/catalog.json").read_text(
                    encoding="utf-8"
                )
            )
            kind = "latex" if stem == "27_advanced_latex" else "mathml"
            content.extend(
                [
                    "## "
                    + (
                        "Equation input files" if language == "en" else "수식 입력 파일"
                    ),
                    "",
                ]
            )
            for entry in inputs:
                if entry["format"] == kind:
                    url = (
                        "https://github.com/joongi007/mathml2docx/blob/master/examples/assets/advanced-math/"
                        + entry["file"]
                    )
                    content.append(f"- [{entry['id']}: {entry['title']}]({url})")
            label = (
                "Independent answers (JSON)" if language == "en" else "독립 정답 (JSON)"
            )
            content.extend(
                [
                    "",
                    f"[{label}](https://github.com/joongi007/mathml2docx/blob/master/tests/fixtures/advanced_math_expectations.json)",
                    "",
                ]
            )
        (gallery / (stem + ".md")).write_text("\n".join(content), encoding="utf-8")
        overview.append(f"- [{title}]({stem}.md): {description}")
    (gallery / "00-index.md").write_text("\n".join(overview) + "\n", encoding="utf-8")


def source_pages(docs):
    pages = [docs / "index.md"] + sorted(docs.glob("[0-9][0-9]-*.md"))
    pages += sorted((docs / "examples").glob("*.md"))
    return {path.relative_to(docs).as_posix() for path in pages}


def main():
    from site_builder import build_static_site, validate_site

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    output = args.output.resolve()
    if output != ROOT / "site" and (
        output == ROOT or ROOT in output.parents or output in ROOT.parents
    ):
        parser.error("Use site/ or a generated directory outside the repository")
    if output.exists() and not (
        (output / ".nojekyll").is_file() and (output / "sitemap.xml").is_file()
    ):
        parser.error("Refusing to replace a directory without generated-site markers")
    docs = ROOT / "docs"
    catalogs = {
        language: json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
        for language, name in [("en", "catalog.json"), ("ko", "catalog.ko.json")]
    }
    if catalogs["en"].keys() != catalogs["ko"].keys():
        raise ValueError("English and Korean catalogs must cover the same examples")
    page_sets = {}
    for language in ("en", "ko"):
        local_docs = docs if language == "en" else docs / "ko"
        example_pages(language, local_docs, catalogs[language])
        page_sets[language] = source_pages(local_docs)
    if page_sets["en"] != page_sets["ko"]:
        raise ValueError(
            "Missing translated pages: " + str(page_sets["en"] ^ page_sets["ko"])
        )
    with tempfile.TemporaryDirectory(prefix="mathml2docx-site-") as tmp:
        stage = Path(tmp) / "site"
        downloads = stage / "downloads"
        downloads.mkdir(parents=True)
        subprocess.run(
            [sys.executable, "-m", "examples.run_all"],
            cwd=ROOT,
            env=dict(
                os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=str(downloads / "examples")
            ),
            check=True,
            stdout=subprocess.DEVNULL,
        )
        with ZipFile(
            downloads / "mathml2docx-examples.zip", "w", ZIP_DEFLATED
        ) as archive:
            for path in sorted((ROOT / "examples").rglob("*")):
                if (
                    path.is_file()
                    and "output" not in path.parts
                    and "__pycache__" not in path.parts
                ):
                    archive.write(path, path.relative_to(ROOT))
            for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
                archive.write(ROOT / name, name)
        shutil.copytree(docs / "assets", stage / "assets")
        shutil.copytree(stage / "assets", stage / "ko/assets")
        shutil.copytree(downloads, stage / "ko/downloads")
        build_static_site(ROOT, stage, page_sets["en"])
        validate_site(stage, page_sets["en"])
        # Only replace the published build after generation and link checks pass.
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    print("Built custom static documentation:", output)


if __name__ == "__main__":
    main()
