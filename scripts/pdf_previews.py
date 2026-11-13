"""Render reference PDF pages for portable, script-free documentation previews."""

import base64
import json
from io import BytesIO

from scripts.example_previews import browser_document


def render_pdf_previews(source, output):
    import pypdfium2 as pdfium

    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for path in sorted(source.glob("[0-9][0-9]_*.pdf")):
        fragments = [
            "<style>body {margin:0;padding:12px;color-scheme:light;"
            "background:Canvas;color:CanvasText;font-family:system-ui,sans-serif}"
            "img {display:block;width:100%;height:auto}"
            "p {margin:18px 0 8px;font-size:12px;text-align:center}</style>"
        ]
        with pdfium.PdfDocument(path) as document:
            count = len(document)
            if not count:
                raise ValueError("PDF has no pages: " + path.name)
            for index in range(count):
                page = document[index]
                try:
                    bitmap = page.render(scale=1.5)
                    try:
                        with bitmap.to_pil() as image, BytesIO() as buffer:
                            image.save(buffer, format="PNG", optimize=True)
                            data = base64.b64encode(buffer.getvalue()).decode()
                            width, height = image.size
                    finally:
                        bitmap.close()
                finally:
                    page.close()
                label = str(index + 1) + " / " + str(count)
                fragments.append(
                    "<p>"
                    + label
                    + '</p><img alt="PDF page '
                    + label
                    + '" width="'
                    + str(width)
                    + '" height="'
                    + str(height)
                    + '" loading="'
                    + ("eager" if index == 0 else "lazy")
                    + '" src="data:image/png;base64,'
                    + data
                    + '">'
                )
        (output / (path.stem + ".html")).write_text(
            browser_document(fragments, path.stem + " PDF"), encoding="utf-8"
        )
        manifest[path.stem] = {"pages": count}
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
