"""Optional Markdown frontend with tables, fenced code and strikethrough."""


def markdown_to_html(source):
    try:
        import markdown
        from markdown.extensions import Extension
        from markdown.inlinepatterns import SimpleTagInlineProcessor
    except ImportError as exc:
        raise ImportError("Install mathml2docx[markdown] to convert Markdown") from exc

    class StrikeExtension(Extension):
        def extendMarkdown(self, md):
            md.inlinePatterns.register(
                SimpleTagInlineProcessor(r"(~~)(?=\S)(.+?)(?<=\S)\1", "del"),
                "mathml2docx_strikethrough",
                175,
            )

    return markdown.markdown(
        source, extensions=["tables", "fenced_code", StrikeExtension()]
    )
