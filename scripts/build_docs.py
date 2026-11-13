"""Build English/Korean documentation and runnable example downloads."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape
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
        "local": "Download and extract the ZIP, then run the following commands from the folder containing `examples/`. The bundle includes helper modules and assets used by the examples.",
        "requirements": "Running all examples requires Python 3.6.2+ for LaTeX. Example 17 also uses docxtpl, included in the installation command below.",
        "output": "Outputs go to `examples/output/`. To run one example, use `python -m examples.01_quickstart`. The commands use the published PyPI package.",
        "setup": "Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:",
        "previews": "Open an example to compare its HTML/MathML in the browser with the LibreOffice PDF output. Use the DOCX download to edit equations in Word. Fonts and document applications can change line wrapping and pagination.",
        "notes": "Visual comparison notes",
        "limits": "Some equation properties vary between Word and LibreOffice, particularly phantom spacing, bevelled fractions and string quotes. Compare the input with the generated document when those details matter.",
        "validation": "Validation scope and limitations",
        "compare": "Compare input and output",
        "browser": "Browser · HTML / MathML",
        "rendered": "LibreOffice · PDF",
        "open_html": "Open HTML preview",
        "open_pdf": "Open PDF",
        "compare_note": "Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.",
        "compare_details": "For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.",
        "partial": "This example also builds content directly in Word. The browser panel shows only the inserted HTML/MathML fragments, in call order; the PDF includes the surrounding Word document and its styles.",
        "no_html": "This example applies styles directly to Word objects and has no HTML input. Its result is shown in the PDF.",
        "pdf_help": "The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.",
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
        "local": "ZIP을 내려받아 압축을 풀고, `examples/` 폴더가 들어 있는 위치에서 아래 명령을 실행하세요. 예제에서 사용하는 공통 모듈과 자산도 ZIP에 포함됩니다.",
        "requirements": "전체 예제를 실행하려면 LaTeX를 위해 Python 3.6.2 이상이 필요합니다. 17번 예제는 docxtpl도 사용하며 아래 설치 명령에 포함되어 있습니다.",
        "output": "결과는 `examples/output/`에 저장됩니다. 개별 예제는 `python -m examples.01_quickstart`처럼 실행하세요. 명령은 PyPI 배포 패키지를 사용하며, 두 언어 문서가 실행 코드를 공유합니다.",
        "setup": "[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.",
        "previews": "예제를 열면 브라우저의 HTML/MathML과 LibreOffice에서 만든 PDF를 비교할 수 있습니다. Word에서 수식을 편집하려면 DOCX를 내려받으세요. 글꼴과 문서 프로그램에 따라 줄바꿈·페이지 배치가 달라질 수 있습니다.",
        "notes": "화면 비교 시 참고할 점",
        "limits": "phantom의 예약 공간, 기울어진 분수, 문자열 따옴표 등은 Word와 LibreOffice에서 다르게 표시될 수 있습니다. 이런 세부 표현이 중요하면 입력과 생성된 문서를 함께 비교하세요.",
        "validation": "검증 범위와 한계",
        "compare": "입력과 출력 비교",
        "browser": "브라우저 · HTML / MathML",
        "rendered": "LibreOffice · PDF",
        "open_html": "HTML 미리보기 열기",
        "open_pdf": "PDF 열기",
        "compare_note": "실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.",
        "compare_details": "Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.",
        "partial": "이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.",
        "no_html": "이 예제는 Word 객체에 직접 스타일을 적용하므로 HTML 입력이 없습니다. PDF에서 결과를 확인하세요.",
        "pdf_help": "PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.",
    },
}


def comparison(stem, text, preview):
    panels = []
    if preview["kind"] != "none":
        url = "../assets/inputs/" + stem + ".html"
        panels.append(
            '<section class="example-preview"><div class="preview-heading">'
            "<h3>"
            + text["browser"]
            + '</h3><a href="'
            + url
            + '">'
            + text["open_html"]
            + '</a></div><iframe src="'
            + url
            + '" title="'
            + escape(text["browser"], quote=True)
            + '" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe>'
            "</section>"
        )
    pdf = ROOT / "docs/assets/previews" / (stem + ".pdf")
    if pdf.is_file():
        url = "../assets/previews/" + stem + ".pdf"
        panels.append(
            '<section class="example-preview"><div class="preview-heading">'
            "<h3>"
            + text["rendered"]
            + '</h3><a href="'
            + url
            + '">'
            + text["open_pdf"]
            + '</a></div><iframe src="'
            + "../assets/pdf-pages/"
            + stem
            + ".html"
            + '" title="'
            + escape(text["rendered"], quote=True)
            + '" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe>'
            "</section>"
        )
    note = text["compare_note"]
    if preview["kind"] == "fragments":
        note += " " + text["partial"]
    elif preview["kind"] == "none":
        note = text["no_html"]
    return [
        "## " + text["compare"],
        "",
        note,
        "",
        '<div class="example-comparison">' + "\n".join(panels) + "</div>",
        "",
        text["compare_details"],
        "",
        text["pdf_help"],
        "",
    ]


def fenced_block(language, source):
    length = max([2] + [len(run) for run in re.findall(r"`+", source)]) + 1
    fence = "`" * length
    return [fence + language, source.rstrip(), fence]


def example_pages(language, docs, catalog, previews):
    text = COPY[language]
    gallery = docs / "examples"
    gallery.mkdir(exist_ok=True)
    overview = [
        "# " + text["overview"],
        "",
        text["intro"].format(count=len(catalog)),
        "",
        f"[{text['zip']}](../downloads/mathml2docx-examples.zip)",
        "",
        text["local"],
        "",
        text["requirements"],
        "",
        "```sh",
        'python -m pip install "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"',
        "python -m examples.run_all",
        "```",
        "",
        text["output"],
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
            *comparison(stem, text, previews[stem]),
            "## " + text["run"],
            "",
            text["setup"],
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
            ["## " + text["source"], "", *fenced_block("python", source), ""]
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
    from site_builder import build_static_site, validate_readme_links, validate_site

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
    with tempfile.TemporaryDirectory(prefix="mathml2docx-site-") as tmp:
        stage = Path(tmp) / "site"
        downloads = stage / "downloads"
        downloads.mkdir(parents=True)
        inputs = stage / "assets/inputs"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.example_previews",
                "--output",
                str(downloads / "examples"),
                "--previews",
                str(inputs),
                "--pdf-source",
                str(docs / "assets/previews"),
            ],
            cwd=ROOT,
            env=dict(
                os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=str(downloads / "examples")
            ),
            check=True,
            stdout=subprocess.DEVNULL,
        )
        previews = json.loads((inputs / "manifest.json").read_text(encoding="utf-8"))
        if previews.keys() != catalogs["en"].keys():
            raise ValueError("Every example needs an input-preview status")
        page_sets = {}
        for language in ("en", "ko"):
            local_docs = docs if language == "en" else docs / "ko"
            example_pages(language, local_docs, catalogs[language], previews)
            page_sets[language] = source_pages(local_docs)
        if page_sets["en"] != page_sets["ko"]:
            raise ValueError("Missing translated pages")
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
        shutil.copytree(docs / "assets", stage / "assets", dirs_exist_ok=True)
        pdfs = json.loads(
            (stage / "assets/pdf-pages/manifest.json").read_text(encoding="utf-8")
        )
        if pdfs.keys() != catalogs["en"].keys():
            raise ValueError("Every example needs a rendered reference PDF")
        shutil.copytree(stage / "assets", stage / "ko/assets")
        shutil.copytree(downloads, stage / "ko/downloads")
        build_static_site(ROOT, stage, page_sets["en"])
        validate_site(stage, page_sets["en"])
        validate_readme_links(
            stage,
            [
                ROOT / "README.md",
                ROOT / "README.ko.md",
                ROOT / "examples/README.md",
                ROOT / "examples/README.ko.md",
            ],
        )
        # Only replace the published build after generation and link checks pass.
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    print("Built custom static documentation:", output)


if __name__ == "__main__":
    main()
