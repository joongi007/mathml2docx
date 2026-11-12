"""Render the documentation's Markdown into a portable bilingual static site."""

import json
import posixpath
import shutil
from html import escape
from urllib.parse import unquote, urlsplit, urlunsplit

from bs4 import BeautifulSoup

SITE_URL = "https://joongi007.github.io/mathml2docx/"
REPO = "https://github.com/joongi007/mathml2docx"
COPY = {
    "en": dict(
        label="Documentation",
        search="Search documentation",
        searching="Searching…",
        empty="No matching pages. Try a function or option name.",
        failed="Search could not load. Browse the navigation or try again.",
        count="results",
        contents="On this page",
        menu="Menu",
        skip="Skip to content",
        previous="Previous",
        next="Next",
        edit="Edit this page",
        copy="Copy",
        copied="Copied",
        copy_failed="Select and copy the code.",
        navigation="Documentation navigation",
        language="Language",
        close="Clear search",
        footer="HTML, MathML and LaTeX to editable Word documents.",
    ),
    "ko": dict(
        label="문서",
        search="문서 검색",
        searching="검색 중…",
        empty="검색 결과가 없습니다. 함수나 옵션 이름으로 검색해 보세요.",
        failed="검색을 불러오지 못했습니다. 목차를 이용하거나 다시 시도해 주세요.",
        count="개 결과",
        contents="이 페이지의 내용",
        menu="목차",
        skip="본문으로 이동",
        previous="이전",
        next="다음",
        edit="이 페이지 수정",
        copy="복사",
        copied="복사됨",
        copy_failed="코드를 선택해 복사해 주세요.",
        navigation="문서 목차",
        language="언어",
        close="검색 지우기",
        footer="HTML·MathML·LaTeX를 편집 가능한 Word 문서로 변환합니다.",
    ),
}


def page_url(source):
    return "" if source == "index.md" else source[:-3] + "/"


def relative(target, current):
    return posixpath.relpath(target or ".", current or ".") + (
        "/" if not target or target.endswith("/") else ""
    )


def rewrite_links(html, source, pages):
    """Resolve Markdown-relative references before moving each page to a folder."""
    soup = BeautifulSoup(html, "html.parser")
    current = page_url(source)
    for tag, attr in [("a", "href"), ("img", "src")]:
        for node in soup.find_all(tag):
            value = node.get(attr, "")
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path or value.startswith("/"):
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(source), unquote(parts.path))
            )
            if target.startswith("../"):
                raise ValueError(
                    "Reference escapes documentation: " + source + ": " + value
                )
            if target.endswith(".md"):
                if target not in pages:
                    raise ValueError(
                        "Unknown documentation page: " + source + ": " + value
                    )
                target = page_url(target)
            node[attr] = urlunsplit(
                ("", "", relative(target, current), parts.query, parts.fragment)
            )
    for table in soup.find_all("table"):
        wrapper = soup.new_tag(
            "div",
            attrs={
                "class": "table-scroll",
                "tabindex": "0",
                "role": "region",
                "aria-label": "Table" if not source.startswith("ko/") else "표",
            },
        )
        table.wrap(wrapper)
    return str(soup)


def build_static_site(root, site, pages):
    import markdown
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
    from pygments.formatters import HtmlFormatter

    theme = root / "docs_site"
    env = Environment(
        loader=FileSystemLoader(str(theme)),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
    )
    template = env.get_template("page.html")
    nav = json.loads((theme / "navigation.json").read_text(encoding="utf-8"))
    assets = site / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for path in theme.glob("*.css"):
        shutil.copy2(path, assets / path.name)
    shutil.copy2(theme / "site.js", assets / "site.js")
    (assets / "syntax.css").write_text(
        HtmlFormatter(style="friendly").get_style_defs(".codehilite"), encoding="utf-8"
    )
    sitemap = []
    for language, prefix in [("en", ""), ("ko", "ko/")]:
        index = []
        local_docs = root / "docs" / prefix
        ordered = [p for group in nav[language] for p in group["pages"]]
        paths = [p[1] for p in ordered]
        if set(paths) != pages or len(paths) != len(set(paths)):
            raise ValueError(
                "Navigation must list every page exactly once: " + language
            )
        for source in sorted(pages):
            current = prefix + page_url(source)
            md = markdown.Markdown(
                extensions=["fenced_code", "tables", "toc", "codehilite"],
                extension_configs={
                    "toc": {"permalink": False},
                    "codehilite": {"guess_lang": False},
                },
            )
            rendered = md.convert((local_docs / source).read_text(encoding="utf-8"))
            rendered = rewrite_links(rendered, source, pages)
            soup = BeautifulSoup(rendered, "html.parser")
            headings = soup.find_all("h1")
            if len(headings) != 1:
                raise ValueError("Each page needs one h1: " + source)
            title = headings[0].get_text(" ", strip=True)
            description_node = soup.find("p")
            description = (
                description_node.get_text(" ", strip=True)
                if description_node
                else title
            )
            for n in soup.find_all("a", class_="headerlink"):
                n.decompose()
            # Index individual sections for useful snippets on long reference pages.
            for section in soup.find_all(["h1", "h2", "h3"]):
                texts = []
                for sibling in section.next_siblings:
                    if getattr(sibling, "name", None) in {"h1", "h2", "h3"}:
                        break
                    texts.append(
                        sibling.get_text(" ", strip=True)
                        if hasattr(sibling, "get_text")
                        else str(sibling)
                    )
                index.append(
                    {
                        "title": title,
                        "heading": section.get_text(" ", strip=True),
                        "text": " ".join(texts),
                        "location": page_url(source)
                        + ("#" + section["id"] if section.get("id") else ""),
                    }
                )
            groups = [
                {
                    "title": g["title"],
                    "pages": [
                        {
                            "title": label,
                            "href": relative(prefix + page_url(path), current),
                            "current": path == source,
                        }
                        for label, path in g["pages"]
                    ],
                }
                for g in nav[language]
            ]
            position = paths.index(source)

            def neighbor(
                offset,
                position=position,
                ordered=ordered,
                prefix=prefix,
                current=current,
            ):
                at = position + offset
                if not 0 <= at < len(ordered):
                    return None
                label, path = ordered[at]
                return {
                    "title": label,
                    "href": relative(prefix + page_url(path), current),
                }

            languages = [
                {
                    "code": code,
                    "label": "English" if code == "en" else "한국어",
                    "href": relative(pre + page_url(source), current),
                    "absolute": SITE_URL + pre + page_url(source),
                    "current": code == language,
                }
                for code, pre in [("en", ""), ("ko", "ko/")]
            ]
            toc = [
                dict(
                    id=tag["id"],
                    title=tag.get_text(" ", strip=True),
                    level=int(tag.name[1]),
                )
                for tag in soup.find_all(["h2", "h3"])
                if tag.get("id")
            ]
            output = template.render(
                language=language,
                text=COPY[language],
                title=title,
                description=description[:180],
                canonical=SITE_URL + current,
                languages=languages,
                nav=groups,
                toc=toc,
                content=str(soup),
                assets=relative("assets/", current),
                home=relative(prefix, current),
                locale_base=relative(prefix, current),
                search_index=relative(prefix + "search/search_index.json", current),
                repo=REPO,
                edit_url=REPO + "/edit/master/docs/" + prefix + source,
                previous=neighbor(-1),
                next=neighbor(1),
            )
            destination = site / current / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output, encoding="utf-8")
            sitemap.append(SITE_URL + current)
        search = site / prefix / "search/search_index.json"
        search.parent.mkdir(parents=True, exist_ok=True)
        search.write_text(
            json.dumps(
                {"config": {"lang": [language]}, "docs": index}, ensure_ascii=False
            ),
            encoding="utf-8",
        )
    (site / ".nojekyll").touch()
    (site / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join("<url><loc>" + escape(url) + "</loc></url>" for url in sitemap)
        + "</urlset>",
        encoding="utf-8",
    )
    (site / "404.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Page not found · mathml2docx</title><h1>Page not found</h1><p><a href="'
        + SITE_URL
        + '">Open the documentation</a></p></html>',
        encoding="utf-8",
    )


def validate_site(site, pages):
    """Fail on broken pages, anchors, translations, search or example downloads."""
    ids = {}
    for path in site.rglob("*.html"):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        page_ids = [n["id"] for n in soup.find_all(id=True)]
        if len(page_ids) != len(set(page_ids)):
            raise ValueError("Duplicate HTML IDs: " + str(path))
        ids[path.resolve()] = set(page_ids)
    checked = 0
    for language, prefix in [("en", ""), ("ko", "ko/")]:
        search = json.loads(
            (site / prefix / "search/search_index.json").read_text(encoding="utf-8")
        )
        if search["config"]["lang"] != [language] or not search["docs"]:
            raise ValueError("Missing localized search")
        for source in pages:
            path = site / prefix / page_url(source) / "index.html"
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            if "&lt;built-in" in str(soup) or "built-in method" in str(soup):
                raise ValueError("Invalid template dictionary lookup: " + str(path))
            if soup.html["lang"] != language or len(soup.select("main h1")) != 1:
                raise ValueError("Invalid language or page title: " + str(path))
            language_links = soup.select("a[hreflang]")
            if len(language_links) != 2 or [
                n["hreflang"] for n in language_links if n.get("aria-current") == "page"
            ] != [language]:
                raise ValueError("Invalid language switcher: " + str(path))
            for node in soup.select("[href], [src]"):
                value = node.get("href", node.get("src", ""))
                parts = urlsplit(value)
                if parts.scheme or parts.netloc or value.startswith("/"):
                    continue
                target = (
                    (path.parent / unquote(parts.path)).resolve()
                    if parts.path
                    else path.resolve()
                )
                if target.is_dir():
                    target /= "index.html"
                if not target.is_file():
                    raise ValueError(
                        "Broken site link: "
                        + str(path.relative_to(site))
                        + ": "
                        + value
                    )
                if (
                    parts.fragment
                    and target.suffix == ".html"
                    and unquote(parts.fragment) not in ids.get(target, set())
                ):
                    raise ValueError(
                        "Broken anchor: " + str(path.relative_to(site)) + ": " + value
                    )
                checked += 1
            for link in language_links:
                other = "ko/" if link["hreflang"] == "ko" else ""
                expected = site / other / page_url(source) / "index.html"
                actual = (path.parent / link["href"] / "index.html").resolve()
                if actual != expected.resolve():
                    raise ValueError("Incorrect equivalent language page: " + str(path))
        if not (site / prefix / "downloads/mathml2docx-examples.zip").is_file():
            raise ValueError("Missing source downloads")
    print(
        "Verified",
        len(pages),
        "paired pages and",
        checked,
        "local links/anchors; localized search and downloads.",
    )
