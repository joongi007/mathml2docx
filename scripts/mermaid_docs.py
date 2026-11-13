"""Render Mermaid fences in opaque sandbox frames with a pinned local bundle."""

import base64
import hashlib
import io
import re
import tarfile
from html import escape
from urllib.request import urlopen

VERSION = "12.3.0"
ARCHIVE = "https://registry.npmjs.org/mermaid/-/mermaid-12.3.0.tgz"
INTEGRITY = "4113TdXeLAsMruJ79OpFL5O8+LTFXhQqZ260rF3tgUmiNAtRm4Uume04I+65PRN6yZ69J4f8rVYWW8zRk65UYw=="
MAX_SOURCE = 20000
BUNDLE_SHA256 = "336df803d87a38b70a01e736e666c8f7601d2ce42f5e47c8fafe5d721074b9a3"
LICENSE_SHA256 = "ec9fb67dcb25eccc416ed56e1aab819222c805a2a4bfe4cb19e7556bf2ffde80"


def mark_mermaid_fences(source):
    """Recognize top-level fences without treating nested code examples as diagrams."""
    result = []
    lines = source.splitlines(keepends=True)
    index = 0
    while index < len(lines):
        opening = re.fullmatch(r" {0,3}(`{3,}|~{3,})([^\n]*)\n?", lines[index])
        if not opening:
            result.append(lines[index])
            index += 1
            continue
        fence, language = opening.groups()
        end = index + 1
        closing = (
            r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*\n?"
        )
        while end < len(lines) and not re.fullmatch(closing, lines[end]):
            end += 1
        if language.strip() == "mermaid" and end < len(lines):
            code = "".join(lines[index + 1 : end]).rstrip()
            if len(code) > MAX_SOURCE:
                raise ValueError("Mermaid diagram exceeds 20,000 characters")
            # Mermaid directives/front matter may otherwise override renderer config.
            if re.search(r"%%\s*\{", code) or code.lstrip().startswith("---"):
                raise ValueError(
                    "Mermaid configuration must be set by the site, not diagrams"
                )
            result.append('<pre class="mermaid-source">' + escape(code) + "</pre>\n")
        else:
            result.extend(lines[index : min(end + 1, len(lines))])
        index = end + 1
    return "".join(result)


def verify_archive(data):
    digest = base64.b64encode(hashlib.sha512(data).digest()).decode()
    if digest != INTEGRITY:
        raise ValueError("Mermaid npm archive integrity mismatch")


def prepare_bundle(assets):
    bundle = assets / ("mermaid-" + VERSION + ".min.js")
    if bundle.exists():
        license_path = assets / "mermaid-LICENSE.txt"
        if hashlib.sha256(bundle.read_bytes()).hexdigest() != BUNDLE_SHA256 or (
            not license_path.is_file()
            or hashlib.sha256(license_path.read_bytes()).hexdigest() != LICENSE_SHA256
        ):
            raise ValueError("Cached Mermaid bundle/license integrity mismatch")
        return
    with urlopen(ARCHIVE, timeout=60) as response:
        data = response.read(40 * 1024 * 1024 + 1)
    if len(data) > 40 * 1024 * 1024:
        raise ValueError("Mermaid archive exceeds download limit")
    verify_archive(data)
    # Read named members only; never extract archive paths into the filesystem.
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        bundle.write_bytes(archive.extractfile("package/dist/mermaid.min.js").read())
        (assets / "mermaid-LICENSE.txt").write_bytes(
            archive.extractfile("package/LICENSE").read()
        )


def render_mermaid(soup, assets, current, relative, language):
    blocks = list(soup.select("pre.mermaid-source"))
    if not blocks:
        return
    prepare_bundle(assets)
    diagrams = assets / "diagrams"
    diagrams.mkdir(exist_ok=True)
    for block in blocks:
        source = block.get_text()
        # Raw HTML cannot bypass the same source/configuration limits.
        if (
            len(source) > MAX_SOURCE
            or re.search(r"%%\s*\{", source)
            or source.lstrip().startswith("---")
        ):
            raise ValueError("Invalid Mermaid source/configuration")
        key = hashlib.sha256(source.encode()).hexdigest()
        title = "Diagram" if language == "en" else "다이어그램"
        viewer = (
            '<!doctype html><html lang="' + language + '"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex">'
            '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; '
            "script-src &#39;self&#39;; style-src &#39;self&#39; &#39;unsafe-inline&#39;; img-src data:; "
            'base-uri &#39;none&#39;; form-action &#39;none&#39;; connect-src &#39;none&#39;">'
            "<title>" + title + '</title><link rel="stylesheet" href="../diagram.css">'
            '<script defer src="../mermaid-' + VERSION + '.min.js"></script>'
            '<script defer src="../diagram.js"></script></head><body>'
            '<p id="diagram-status" role="status">'
            + ("Loading diagram…" if language == "en" else "다이어그램을 불러오는 중…")
            + '</p><div id="diagram"></div><pre id="diagram-source" hidden>'
            + escape(source)
            + "</pre></body></html>"
        )
        name = key + "-" + language + ".html"
        (diagrams / name).write_text(viewer, encoding="utf-8")
        wrapper = soup.new_tag("div", attrs={"class": "mermaid-diagram"})
        frame = soup.new_tag(
            "iframe",
            attrs={
                "class": "mermaid-frame",
                "title": title,
                "src": relative("assets/diagrams/" + name, current),
                "sandbox": "allow-scripts",
                "loading": "lazy",
                "referrerpolicy": "no-referrer",
            },
        )
        wrapper.append(frame)
        details = soup.new_tag("details")
        summary = soup.new_tag("summary")
        summary.string = "Diagram source" if language == "en" else "다이어그램 원문"
        details.append(summary)
        block["class"] = ["mermaid-code"]
        block.wrap(details)
        details.insert_before(wrapper)
