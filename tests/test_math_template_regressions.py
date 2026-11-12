"""Template boundaries preserve mathematical and other non-text XML content."""

import unittest
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

from mathml2docx import MathmlToDocx


def saved_xml(document):
    output = BytesIO()
    document.save(output)
    output.seek(0)
    with ZipFile(output) as archive:
        return etree.fromstring(archive.read("word/document.xml"))


def math_text(document):
    return [node.text for node in saved_xml(document).iter(qn("m:t"))]


def endpoint(name, identifier="42"):
    node = OxmlElement("w:bookmark" + name)
    node.set(qn("w:id"), identifier)
    if name == "Start":
        node.set(qn("w:name"), "equation")
    return node


def equation(value):
    document = MathmlToDocx().parse_mathml("<math><mi>" + value + "</mi></math>")
    return deepcopy(document.paragraphs[0]._p.find(qn("m:oMath")))


class MathematicalMarkerTests(unittest.TestCase):
    def test_adjacent_equations_survive_inline_and_block_replacements(self):
        for left, right in ((True, False), (False, True), (True, True)):
            for replacement in (
                "<b>new</b>",
                "<p>new</p>",
                "<math display='block'><mi>z</mi></math>",
            ):
                for reopen in (False, True):
                    with self.subTest(
                        left=left, right=right, replacement=replacement, reopen=reopen
                    ):
                        source = "<math><mi>x</mi></math>" if left else ""
                        source += "{{value}}"
                        source += "<math><mi>y</mi></math>" if right else ""
                        document = MathmlToDocx().convert(source)
                        if reopen:
                            output = BytesIO()
                            document.save(output)
                            output.seek(0)
                            document = Document(output)
                        MathmlToDocx().replace_html(document, "{{value}}", replacement)
                        expected = ["x"] if left else []
                        if "<math" in replacement:
                            expected.append("z")
                        expected += ["y"] if right else []
                        self.assertEqual(math_text(document), expected)

    def test_interleaved_math_picture_break_and_bookmarks_survive(self):
        for replacement in ("new", "<p>new</p>"):
            with self.subTest(replacement=replacement):
                document = Document()
                paragraph = document.add_paragraph()
                paragraph.add_run("before {{va").bold = True
                paragraph._p.append(equation("x"))
                paragraph.add_run().add_picture(str(Path("examples/assets/swatch.png")))
                paragraph.add_run().add_break()
                paragraph._p.append(endpoint("Start", "7"))
                paragraph._p.append(endpoint("End", "7"))
                paragraph.add_run("lue}} after").italic = True
                MathmlToDocx().replace_html(document, "{{value}}", replacement)
                root = saved_xml(document)
                self.assertEqual(math_text(document), ["x"])
                for tag in ("w:drawing", "w:br", "w:bookmarkStart", "w:bookmarkEnd"):
                    self.assertEqual(len(list(root.iter(qn(tag)))), 1, tag)
                self.assertEqual(
                    "".join(node.text or "" for node in root.iter(qn("w:t"))),
                    "before new after",
                )
                before = next(
                    node
                    for node in root.iter(qn("w:r"))
                    if "before" in "".join(node.itertext())
                )
                after = next(
                    node
                    for node in root.iter(qn("w:r"))
                    if "after" in "".join(node.itertext())
                )
                self.assertIsNotNone(before.find(qn("w:rPr")).find(qn("w:b")))
                self.assertIsNotNone(after.find(qn("w:rPr")).find(qn("w:i")))

    def test_equation_and_explicit_break_only_sides_survive_block_insertion(self):
        document = MathmlToDocx().convert(
            "<math><mi>x</mi></math>{{value}}<math><mi>y</mi></math>"
        )
        document.paragraphs[0].add_run().add_break()
        MathmlToDocx().replace_html(
            document, "{{value}}", "<table><tr><td>new</td></tr></table>"
        )
        self.assertEqual(math_text(document), ["x", "y"])
        self.assertEqual(len(list(saved_xml(document).iter(qn("w:br")))), 1)
        self.assertEqual(len(document.tables), 1)

    def test_marker_inside_hyperlink_preserves_equations_and_run_formatting(self):
        document = MathmlToDocx().convert(
            '<a href="https://example.com"><b>before {{va</b>'
            "<math><mi>x</mi></math><i>lue}} after</i></a>"
        )
        MathmlToDocx().replace_html(document, "{{value}}", "<p>new</p>")
        self.assertEqual(math_text(document), ["x"])
        root = saved_xml(document)
        links = list(root.iter(qn("w:hyperlink")))
        self.assertEqual(len(links), 3)
        self.assertEqual(len({node.get(qn("r:id")) for node in links}), 1)
        self.assertEqual(
            "".join(node.text or "" for node in root.iter(qn("w:t"))),
            "before new after",
        )


class MathematicalBookmarkTests(unittest.TestCase):
    def test_equation_only_bookmark_replaces_selected_math(self):
        for replacement in (
            "<math><mi>y</mi></math>",
            "<p><math><mi>y</mi></math></p>",
        ):
            with self.subTest(replacement=replacement):
                document = Document()
                paragraph = document.add_paragraph()
                paragraph._p.extend(
                    [
                        equation("a"),
                        endpoint("Start"),
                        equation("x"),
                        endpoint("End"),
                        equation("b"),
                    ]
                )
                MathmlToDocx().replace_bookmark(document, "equation", replacement)
                self.assertEqual(math_text(document), ["a", "y", "b"])
                MathmlToDocx().replace_bookmark(
                    document, "equation", "<math><mi>z</mi></math>"
                )
                self.assertEqual(math_text(document), ["a", "z", "b"])

    def test_bookmark_endpoints_inside_hyperlink_and_runs(self):
        document = Document()
        paragraph = document.add_paragraph()
        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("w:anchor"), "destination")
        paragraph._p.append(hyperlink)
        first = OxmlElement("w:r")
        props = OxmlElement("w:rPr")
        props.append(OxmlElement("w:b"))
        first.append(props)
        text = OxmlElement("w:t")
        text.text = "before"
        first.append(text)
        last = OxmlElement("w:r")
        text = OxmlElement("w:t")
        text.text = "after"
        last.append(text)
        hyperlink.extend(
            [first, endpoint("Start"), equation("x"), endpoint("End"), last]
        )
        MathmlToDocx().replace_bookmark(document, "equation", "<math><mi>y</mi></math>")
        self.assertEqual(math_text(document), ["y"])
        root = saved_xml(document)
        links = list(root.iter(qn("w:hyperlink")))
        self.assertEqual(
            [
                "".join(node.text or "" for node in link.iter(qn("w:t")))
                for link in links
            ],
            ["before", "after"],
        )
        self.assertIsNotNone(links[0].find(".//" + qn("w:b")))

    def test_cross_paragraph_range_removes_equations_and_table_inside_range(self):
        document = Document()
        first = document.add_paragraph()
        first._p.extend([equation("a"), endpoint("Start"), equation("x")])
        document.add_table(1, 1).cell(0, 0).text = "old table"
        last = document.add_paragraph()
        last._p.extend([equation("q"), endpoint("End"), equation("b")])
        MathmlToDocx().replace_bookmark(
            document, "equation", "<p><math><mi>y</mi></math></p>"
        )
        self.assertEqual(math_text(document), ["a", "y", "b"])
        self.assertFalse(document.tables)

    def test_bookmark_inside_content_control_preserves_control_properties(self):
        document = Document()
        paragraph = document.add_paragraph()
        control = OxmlElement("w:sdt")
        props = OxmlElement("w:sdtPr")
        tag = OxmlElement("w:tag")
        tag.set(qn("w:val"), "kept")
        props.append(tag)
        content = OxmlElement("w:sdtContent")
        content.extend(
            [
                equation("a"),
                endpoint("Start"),
                equation("x"),
                endpoint("End"),
                equation("b"),
            ]
        )
        control.extend([props, content])
        paragraph._p.append(control)
        MathmlToDocx().replace_bookmark(document, "equation", "<math><mi>y</mi></math>")
        self.assertEqual(math_text(document), ["a", "y", "b"])
        controls = list(saved_xml(document).iter(qn("w:sdt")))
        self.assertEqual(len(controls), 2)
        for node in controls:
            self.assertEqual(
                node.find(qn("w:sdtPr")).find(qn("w:tag")).get(qn("w:val")), "kept"
            )

    def test_reversed_equation_only_endpoints_rejected_without_mutation(self):
        document = Document()
        paragraph = document.add_paragraph()
        paragraph._p.extend([endpoint("End"), equation("x"), endpoint("Start")])
        before = etree.tostring(document._element)
        with self.assertRaises(ValueError):
            MathmlToDocx().replace_bookmark(document, "equation", "new")
        self.assertEqual(etree.tostring(document._element), before)

    def test_invalid_replacement_rolls_back_partial_render_for_both_apis(self):
        for bookmark in (False, True):
            with self.subTest(bookmark=bookmark):
                document = Document()
                paragraph = document.add_paragraph("{{value}}")
                if bookmark:
                    paragraph._p.extend(
                        [endpoint("Start"), equation("x"), endpoint("End")]
                    )
                before = etree.tostring(document._element)
                with self.assertRaises(ValueError):
                    if bookmark:
                        MathmlToDocx().replace_bookmark(
                            document,
                            "equation",
                            "<p>partial</p><math><unknown/></math>",
                        )
                    else:
                        MathmlToDocx().replace_html(
                            document,
                            "{{value}}",
                            "<p>partial</p><math><unknown/></math>",
                        )
                self.assertEqual(etree.tostring(document._element), before)

    def test_failed_render_rolls_back_numbering_image_and_link_relationships(self):
        document = Document()
        document.add_paragraph("{{value}}")

        def package_files():
            output = BytesIO()
            document.save(output)
            output.seek(0)
            with ZipFile(output) as archive:
                return {name: archive.read(name) for name in archive.namelist()}

        before = package_files()
        with self.assertRaises(ValueError):
            MathmlToDocx(img_src_base_path="examples/assets").replace_html(
                document,
                "{{value}}",
                '<ol><li>partial</li></ol><p><a href="https://example.com">link</a>'
                '<img src="swatch.png"></p><math><unknown/></math>',
            )
        self.assertEqual(package_files(), before)


if __name__ == "__main__":
    unittest.main()
