"""Exercise hostile Markdown HTML and Mermaid settings at the publishing boundary."""

import importlib.util

import pytest
from bs4 import BeautifulSoup

from scripts.mermaid_docs import (
    VERSION,
    mark_mermaid_fences,
    prepare_bundle,
    verify_archive,
)
from scripts.site_security import sanitize_document

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("nh3") is None,
    reason="Documentation sanitizer is a docs-only dependency",
)


@pytest.mark.parametrize(
    "href",
    [
        "javascript:alert(1)",
        "jav&#x61;script:alert(1)",
        "java&#10;script:alert(1)",
        "data:text/html,<script>alert(1)</script>",
    ],
)
def test_unsafe_links_are_not_published(href):
    soup = BeautifulSoup(
        sanitize_document('<a href="' + href + '">text</a>'), "html.parser"
    )
    assert soup.a.get("href") is None
    assert soup.a.get_text() == "text"


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script><p>safe</p>",
        '<img src="x" onerror="alert(1)"><p>safe</p>',
        '<svg><a xlink:href="javascript:alert(1)">bad</a></svg><p>safe</p>',
        "<math><mtext><img src=x onerror=alert(1)></mtext></math><p>safe</p>",
        '<style>body {display:none}</style><p style="position:fixed" onclick="alert(1)">safe</p>',
    ],
)
def test_active_markup_and_event_handlers_are_removed(payload):
    soup = BeautifulSoup(sanitize_document(payload), "html.parser")
    assert soup.p.get_text() == "safe"
    assert not soup.find_all(["script", "style", "svg", "math"])
    for tag in soup.find_all(True):
        assert not any(name.startswith("on") or name == "style" for name in tag.attrs)


def test_only_generated_preview_paths_survive_with_forced_empty_sandbox():
    html = """<iframe src="https://example.com" srcdoc="bad"></iframe>
    <iframe src="../assets/inputs/24_dense_report.html" sandbox="allow-scripts allow-same-origin" srcdoc="bad" onload="bad()"></iframe>
    <iframe src="../assets/inputs/../../site.js"></iframe>"""
    soup = BeautifulSoup(sanitize_document(html), "html.parser")
    frames = soup.find_all("iframe")
    assert len(frames) == 1
    assert frames[0]["sandbox"] == []
    assert not frames[0].has_attr("srcdoc")
    assert not frames[0].has_attr("onload")


def test_legitimate_document_content_and_escaped_examples_survive():
    html = '<h2 id="example">Example</h2><pre><code>&lt;script&gt;literal&lt;/script&gt;</code></pre><details><summary>Source</summary>text</details><table><tr><td colspan="2">cell</td></tr></table>'
    soup = BeautifulSoup(sanitize_document(html), "html.parser")
    assert soup.h2["id"] == "example"
    assert soup.code.string == "<script>literal</script>"
    assert soup.summary.string == "Source"
    assert soup.td["colspan"] == "2"


def test_mermaid_fence_escapes_source_and_ignores_nested_code_examples():
    result = mark_mermaid_fences(
        '```mermaid\nflowchart LR\nA["<img onerror=alert(1)>"] --> B\n```\n'
    )
    soup = BeautifulSoup(result, "html.parser")
    assert soup.img is None
    assert "<img onerror=alert(1)>" in soup.pre.get_text()
    nested = "````markdown\n```mermaid\nflowchart LR\nA --> B\n```\n````\n"
    assert mark_mermaid_fences(nested) == nested


@pytest.mark.parametrize(
    "source",
    [
        '%%{init: {"securityLevel":"loose"}}%%\nflowchart LR\nA --> B',
        "---\nconfig:\n  securityLevel: loose\n---\nflowchart LR\nA --> B",
        "flowchart LR\n" + ("x" * 20001),
    ],
)
def test_diagrams_cannot_override_settings_or_exceed_size_bound(source):
    with pytest.raises(ValueError):
        mark_mermaid_fences("```mermaid\n" + source + "\n```\n")


def test_modified_mermaid_archive_is_rejected():
    with pytest.raises(ValueError, match="integrity"):
        verify_archive(b"not the pinned npm package")


def test_nested_markdown_example_stays_entirely_inside_source_code():
    import markdown

    from scripts.build_docs import fenced_block

    source = (
        'text = """# Notes\n```python\nprint(1)\n```\n<script>literal</script>\n"""'
    )
    rendered = markdown.markdown(
        "\n".join(fenced_block("python", source)),
        extensions=["fenced_code", "codehilite"],
    )
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.script is None
    assert soup.pre.get_text().rstrip() == source


def test_tampered_cached_mermaid_bundle_is_rejected(tmp_path):
    (tmp_path / ("mermaid-" + VERSION + ".min.js")).write_text("alert(1)")
    with pytest.raises(ValueError, match="integrity"):
        prepare_bundle(tmp_path)


def test_issue_titles_are_text_and_all_49_reports_remain_linked():
    import re
    from pathlib import Path

    import markdown

    root = Path(__file__).resolve().parents[1]
    for language in ["", "ko"]:
        source = (root / "docs" / language / "07-upstream-audit.md").read_text(
            encoding="utf-8"
        )
        expected = set(
            re.findall(r"https://github.com/pqzx/html2docx/issues/\d+", source)
        )
        soup = BeautifulSoup(
            sanitize_document(markdown.markdown(source, extensions=["tables"])),
            "html.parser",
        )
        actual = {a["href"] for a in soup.find_all("a", href=True)}
        assert len(expected) == 49 and expected <= actual
        assert soup.find("img") is None
