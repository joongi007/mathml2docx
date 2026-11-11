"""Build English/Korean documentation and runnable example downloads."""

import json
import os
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://joongi007.github.io/mathml2docx/"
COPY = {
    "en": {
        "overview": "Runnable examples",
        "intro": "The documentation build executes {count} Python examples to generate DOCX downloads.",
        "run": "Run",
        "docx": "Generated DOCX",
        "pdf": "Reference PDF",
        "source": "Complete source",
        "input": "Input HTML",
        "zip": "All example source and assets (ZIP)",
        "local": "Run from a repository checkout after installing the dependencies above. Local outputs go to `examples/output/`. Run an individual example with, for instance, `python -m examples.01_quickstart`.",
        "previews": "The reference PDFs were rendered with LibreOffice 7.3.7. They are historical previews, not automatically refreshed by this build; Word versions and fonts may produce different results.",
        "notes": "Visual comparison notes",
        "limits": "In the LibreOffice 7.3 reference PDF, M17 phantom width, M19 bevelled fractions, and M20 string quotes differ from the intended display. Their structures, properties, and characters are retained in XML, but visual equivalence has not been established. Direct Microsoft Word checks also remain outstanding.",
        "validation": "Validation scope and limitations",
    },
    "ko": {
        "overview": "실행 예제",
        "intro": "문서 빌드에서 Python 예제 {count}개를 실행해 내려받을 DOCX를 생성합니다.",
        "run": "실행",
        "docx": "생성된 DOCX",
        "pdf": "참조 PDF",
        "source": "전체 코드",
        "input": "입력 HTML",
        "zip": "전체 예제 코드와 자산 (ZIP)",
        "local": "위 의존성을 설치한 뒤 저장소 루트에서 실행하세요. 로컬 결과는 `examples/output/`에 저장됩니다. 개별 예제는 `python -m examples.01_quickstart`처럼 실행할 수 있습니다. 실행 코드는 두 언어 문서가 공유합니다.",
        "previews": "참조 PDF는 LibreOffice 7.3.7에서 렌더링한 과거 미리보기이며, 이번 빌드에서 자동으로 갱신하지 않습니다. Word 버전과 글꼴에 따라 결과가 달라질 수 있습니다.",
        "notes": "화면 비교 시 참고할 점",
        "limits": "LibreOffice 7.3 참조 PDF에서 M17의 phantom 예약 폭, M19의 bevelled 분수, M20의 문자열 따옴표는 의도한 표시와 다릅니다. 구조·속성·문자는 XML에 보존되지만 화면 동등성은 확인하지 못했습니다. Microsoft Word에서 직접 확인하는 작업도 남아 있습니다.",
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
        (gallery / (stem + ".md")).write_text("\n".join(content), encoding="utf-8")
        overview.append(f"- [{title}]({stem}.md): {description}")
    (gallery / "00-index.md").write_text("\n".join(overview) + "\n", encoding="utf-8")


def source_pages(docs):
    pages = [docs / "index.md"] + sorted(docs.glob("[0-9][0-9]-*.md"))
    pages += sorted((docs / "examples").glob("*.md"))
    return {path.relative_to(docs).as_posix() for path in pages}


class LanguageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.language = None
        self.links = {}
        self.current = []
        self.alternates = {}
        self.edit_url = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "a" and "hreflang" in attrs:
            self.links[attrs["hreflang"]] = attrs["href"]
            if attrs.get("aria-current") == "page":
                self.current.append(attrs["hreflang"])
        if tag == "a" and attrs.get("href", "").startswith(
            "https://github.com/joongi007/mathml2docx/edit/"
        ):
            self.edit_url = attrs["href"]
        if tag == "link" and attrs.get("rel") == "alternate":
            self.alternates[attrs["hreflang"]] = attrs["href"]


def validate_site(pages):
    """Check real output: locale, equivalent-page links, search and downloads."""
    site = ROOT / "site"
    for language, prefix in (("en", ""), ("ko", "ko/")):
        for source in pages:
            suffix = "" if source == "index.md" else source.removesuffix(".md") + "/"
            html = site / prefix / suffix / "index.html"
            parser = LanguageLinks()
            parser.feed(html.read_text(encoding="utf-8"))
            if parser.language != language or parser.current != [language]:
                raise ValueError(f"Incorrect language/current selector: {html}")
            if parser.edit_url != (
                "https://github.com/joongi007/mathml2docx/edit/master/docs/"
                + prefix
                + source
            ):
                raise ValueError(f"Incorrect edit source: {html}: {parser.edit_url}")
            for target_language, target_prefix in (("en", ""), ("ko", "ko/")):
                href = parser.links[target_language]
                expected = site / target_prefix / suffix / "index.html"
                actual = html.parent / unquote(urlsplit(href).path) / "index.html"
                if actual.resolve() != expected.resolve() or not actual.is_file():
                    raise ValueError(f"Broken language link: {html}: {href}")
                if (
                    parser.alternates[target_language]
                    != SITE_URL + target_prefix + suffix
                ):
                    raise ValueError(f"Incorrect alternate URL: {html}")
            if parser.alternates["x-default"] != SITE_URL + suffix:
                raise ValueError(f"Incorrect default URL: {html}")
        search = json.loads(
            (site / prefix / "search/search_index.json").read_text(encoding="utf-8")
        )
        if language not in search["config"]["lang"] or not search["docs"]:
            raise ValueError(f"Missing {language} search index")
        if not (site / prefix / "downloads/mathml2docx-examples.zip").is_file():
            raise ValueError(f"Missing {language} example download")
    print(
        f"Verified {len(pages)} paired pages: locale, language links, search, downloads."
    )


def main():
    docs = ROOT / "docs"
    assets = docs / "downloads"
    # Downloads are generated outputs; start fresh to avoid publishing stale files.
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir()

    catalogs = {
        language: json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
        for language, name in (("en", "catalog.json"), ("ko", "catalog.ko.json"))
    }
    if catalogs["en"].keys() != catalogs["ko"].keys():
        raise ValueError(
            "English and Korean example catalogs must cover the same examples"
        )
    subprocess.run(
        [sys.executable, "-m", "examples.run_all"],
        cwd=ROOT,
        env=dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=str(assets / "examples")),
        check=True,
        stdout=subprocess.DEVNULL,
    )
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

    page_sets = {}
    for language in ("en", "ko"):
        local_docs = docs if language == "en" else docs / "ko"
        example_pages(language, local_docs, catalogs[language])
        page_sets[language] = source_pages(local_docs)
    if page_sets["en"] != page_sets["ko"]:
        raise ValueError(
            f"Missing translated pages: {page_sets['en'] ^ page_sets['ko']}"
        )
    # Generated copies keep download URLs local to each locale, including local previews.
    # Only one copy of the source binaries is tracked and included in source archives.
    for directory in ("assets", "downloads"):
        target = docs / "ko" / directory
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(docs / directory, target)
    for config in ("mkdocs.yml", "mkdocs.ko.yml"):
        subprocess.run(
            [
                sys.executable,
                "-m",
                "mkdocs",
                "build",
                "--strict",
                "--config-file",
                config,
            ],
            cwd=ROOT,
            check=True,
        )
    validate_site(page_sets["en"])


if __name__ == "__main__":
    main()
