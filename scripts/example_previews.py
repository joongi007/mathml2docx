"""Record real example inputs while generating DOCX, for isolated browser previews.

Instrumentation is confined to this documentation subprocess. It never changes
the converter, example source, returned documents, or normal example execution.
"""

import argparse
import base64
import importlib
import json
import mimetypes
import os
from contextlib import ExitStack
from html import escape
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
# These examples also construct content/styles directly in python-docx.
PARTIAL = {
    "03_existing_document",
    "06_word_styles",
    "12_asset_loader",
    "15_markers",
    "16_bookmarks",
    "17_docxtpl",
    "23_complex_equations",
    "26_template_workbook",
    "27_advanced_latex",
    "30_mathml_fidelity",
}


def inline_assets(source, config=None):
    """Inline local demo resources without fetching arbitrary URLs."""
    if source.lstrip().startswith("<?xml"):
        source = source.lstrip().partition("?>")[2]
    soup = BeautifulSoup(source, "html.parser")
    options = config.options if config is not None else {}
    base = Path(options.get("img_src_base_path") or ROOT / "examples/assets")

    def local_file(value):
        if urlsplit(value).scheme or urlsplit(value).netloc:
            return None
        path = (base / value).resolve()
        assets = (ROOT / "examples/assets").resolve()
        return path if assets in path.parents and path.is_file() else None

    for image in soup.find_all("img", src=True):
        value = image["src"]
        if value.startswith("data:"):
            continue
        loader = options.get("image_loader")
        path = local_file(value)
        if loader is not None:
            data = loader(value)
            if hasattr(data, "getvalue"):
                data = data.getvalue()
        elif path is not None:
            data = path.read_bytes()
        else:
            # Deliberately missing inputs (example 18) stay visibly missing.
            image["alt"] = image.get("alt") or "Unavailable image: " + value
            del image["src"]
            continue
        media = mimetypes.guess_type(value)[0] or "image/png"
        image["src"] = "data:" + media + ";base64," + base64.b64encode(data).decode()
    for link in soup.find_all("link", href=True):
        if "stylesheet" not in link.get("rel", []):
            continue
        loader = getattr(config, "stylesheet_loader", None)
        path = local_file(link["href"])
        css = (
            loader(link["href"])
            if loader
            else (path.read_text(encoding="utf-8") if path else "")
        )
        style = soup.new_tag("style")
        style.string = css
        link.replace_with(style)
    if getattr(config, "stylesheet", ""):
        style = soup.new_tag("style")
        style.string = config.stylesheet
        soup.insert(0, style)
    # Scripts are unnecessary for these static inputs. CSP also isolates opened
    # standalone previews, while the embedding iframe uses an empty sandbox.
    for node in soup.find_all(["script", "base", "meta", "iframe", "object", "embed"]):
        node.decompose()
    for node in soup.find_all(True):
        for key in list(node.attrs):
            if key.startswith("on"):
                del node[key]
    # Combining complete HTML inputs must not nest html/head/body elements.
    for node in list(soup.find_all(["html", "head", "body"])):
        node.unwrap()
    return str(soup)


def browser_document(fragments, title):
    policy = (
        "default-src 'none'; img-src data:; style-src 'unsafe-inline'; "
        "base-uri 'none'; form-action 'none'"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex">'
        '<meta http-equiv="Content-Security-Policy" content="'
        + escape(policy, quote=True)
        + '"><title>'
        + escape(title)
        + "</title></head><body>"
        + "\n".join(fragments)
        + "</body></html>"
    )


class InputRecorder:
    def __init__(self):
        self.fragments = []
        self.depth = 0

    def html_call(self, original):
        def recorded(config, source, *args, **kwargs):
            outer = self.depth == 0
            self.depth += 1
            try:
                result = original(config, source, *args, **kwargs)
            finally:
                self.depth -= 1
            if outer:
                self.fragments.append(inline_assets(source, config))
            return result

        return recorded

    def math_call(self, original):
        def recorded(source, *args, **kwargs):
            result = original(source, *args, **kwargs)
            if self.depth == 0:
                self.fragments.append(inline_assets(source))
            return result

        return recorded

    def install(self, stack):
        import mathml2docx
        from mathml2docx import h2d, math

        stack.enter_context(
            patch.object(
                h2d.HtmlToDocx,
                "add_html_to_document",
                self.html_call(h2d.HtmlToDocx.add_html_to_document),
            )
        )
        recorded_math = self.math_call(math.mathml_to_omml)
        for module in (mathml2docx, math, h2d):
            stack.enter_context(patch.object(module, "mathml_to_omml", recorded_math))


def generate(output, previews):
    os.environ["MATHML2DOCX_EXAMPLE_OUTPUT"] = str(output.resolve())
    previews.mkdir(parents=True, exist_ok=True)
    manifest = {}
    recorder = InputRecorder()
    with ExitStack() as stack:
        recorder.install(stack)
        for path in sorted((ROOT / "examples").glob("[0-9][0-9]_*.py")):
            recorder.fragments = []
            importlib.import_module("examples." + path.stem)
            if recorder.fragments:
                (previews / (path.stem + ".html")).write_text(
                    browser_document(recorder.fragments, path.stem), encoding="utf-8"
                )
                manifest[path.stem] = {
                    "kind": "fragments" if path.stem in PARTIAL else "input",
                    "parts": len(recorder.fragments),
                }
            else:
                manifest[path.stem] = {"kind": "none", "parts": 0}
    (previews / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previews", type=Path, required=True)
    parser.add_argument("--pdf-source", type=Path)
    args = parser.parse_args()
    generate(args.output, args.previews)
    if args.pdf_source:
        from scripts.pdf_previews import render_pdf_previews

        render_pdf_previews(args.pdf_source, args.previews.parent / "pdf-pages")


if __name__ == "__main__":
    main()
