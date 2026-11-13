"""Keep browser inputs independent from DOCX output and isolated from the site."""

from contextlib import ExitStack

from bs4 import BeautifulSoup
from docx import Document

from mathml2docx import MathmlToDocx
from scripts.example_previews import InputRecorder, browser_document, inline_assets
from scripts.site_builder import rewrite_links


def test_record_inputs_once_and_leave_converter_unchanged():
    from mathml2docx import h2d, math

    original = h2d.HtmlToDocx.add_html_to_document
    recorder = InputRecorder()
    with ExitStack() as stack:
        recorder.install(stack)
        parser = MathmlToDocx()
        doc = parser.convert("<p>A<math><mi>x</mi></math>B</p>")
        cell = doc.add_table(rows=1, cols=1).cell(0, 0)
        parser.add_html_to_cell("<b>cell</b>", cell)
        math.mathml_to_omml("<math><mi>y</mi></math>")
        assert len(recorder.fragments) == 3
        assert recorder.fragments[0].count("<math>") == 1
        assert doc._element.xpath("//m:t/text()") == ["x"]
        assert doc.paragraphs[0].text == "AB"
        assert doc.tables[0].cell(0, 0).text == "cell"
    assert h2d.HtmlToDocx.add_html_to_document is original
    assert len(Document().paragraphs) == 0


def test_preview_includes_configured_assets_and_css():
    parser = MathmlToDocx(
        image_loader=lambda name: b"png-bytes",
        stylesheet="h1 {color:navy}",
        stylesheet_loader=lambda name: "p {color:teal}",
    )
    result = BeautifulSoup(
        inline_assets(
            '<link rel="stylesheet" href="theme.css"><img src="asset:logo">', parser
        ),
        "html.parser",
    )
    assert result.img["src"] == "data:image/png;base64,cG5nLWJ5dGVz"
    assert [style.string for style in result.find_all("style")] == [
        "h1 {color:navy}",
        "p {color:teal}",
    ]
    assert result.link is None


def test_standalone_preview_cannot_run_scripts_or_fetch_external_resources():
    fragment = inline_assets(
        '<base href="https://example.com"><script>alert(1)</script>'
        '<p onclick="alert(1)">Input</p><img src="https://example.com/a.png">'
    )
    soup = BeautifulSoup(browser_document([fragment], 'A "title"'), "html.parser")
    assert soup.script is None and soup.base is None
    assert "onclick" not in soup.p.attrs
    assert "src" not in soup.img.attrs
    assert soup.title.string == 'A "title"'
    policy = soup.find("meta", attrs={"http-equiv": "Content-Security-Policy"})
    assert "default-src 'none'" in policy["content"]
    assert soup.find("meta", attrs={"name": "robots"})["content"] == "noindex"


def test_iframe_paths_move_with_english_and_korean_pages():
    for source in ["examples/24_dense_report.md", "ko/examples/24_dense_report.md"]:
        html = '<iframe title="Input" sandbox="" src="../assets/inputs/24_dense_report.html"></iframe>'
        result = BeautifulSoup(rewrite_links(html, source, set()), "html.parser")
        assert result.iframe["src"] == "../../assets/inputs/24_dense_report.html"
        assert result.iframe.has_attr("sandbox")
