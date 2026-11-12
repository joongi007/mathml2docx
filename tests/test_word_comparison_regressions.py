"""Word equivalences retain authored mathematical formatting and layout."""

import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from mathml2docx import MathmlToDocx
from scripts.check_word import compare_word_documents
from tests.docx_oracle import DocxOracle


def reopened(document):
    output = BytesIO()
    document.save(output)
    output.seek(0)
    return Document(output)


def field_document(target="https://example.com/method"):
    document = MathmlToDocx().convert(
        '<math display="block"><mfrac><mn>1</mn><mn>2</mn></mfrac></math>'
    )
    math = document._element.xpath("//m:oMath")[0]

    def marker(kind):
        run = OxmlElement("m:r")
        child = OxmlElement("w:fldChar")
        child.set(qn("w:fldCharType"), kind)
        run.append(child)
        return run

    instruction = OxmlElement("m:r")
    code = OxmlElement("w:instrText")
    code.text = ' HYPERLINK "' + target + '" '
    instruction.append(code)
    math.insert(0, marker("begin"))
    math.insert(1, instruction)
    math.insert(2, marker("separate"))
    math.append(marker("end"))
    return document


class WordComparisonTests(unittest.TestCase):
    def compare(self, original, saved):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "original.docx", Path(tmp) / "saved.docx"
            original.save(str(a))
            saved.save(str(b))
            return compare_word_documents(DocxOracle(a), DocxOracle(b))

    def test_explicit_default_math_font_and_inherited_size_are_equivalent(self):
        original = MathmlToDocx().convert(
            '<math style="font-size:11pt"><mi>x</mi></math>'
        )
        saved = reopened(original)
        run = saved._element.xpath("//m:r")[0]
        props = run.find(qn("w:rPr"))
        props.remove(props.find(qn("w:sz")))
        fonts = OxmlElement("w:rFonts")
        fonts.set(qn("w:ascii"), "Cambria Math")
        fonts.set(qn("w:hAnsi"), "Cambria Math")
        props.insert(0, fonts)
        result = self.compare(original, saved)
        self.assertFalse(result["raw_blocks_match"])
        self.assertTrue(result["effective_blocks_match"])

    def test_explicit_no_underline_and_absent_default_underline_are_equivalent(self):
        original = Document()
        run = original.add_paragraph().add_run("removed")
        run.font.strike = True
        run.underline = False
        saved = reopened(original)
        props = saved.paragraphs[0].runs[0]._r.get_or_add_rPr()
        props.remove(props.find(qn("w:u")))
        result = self.compare(original, saved)
        self.assertFalse(result["raw_blocks_match"])
        self.assertTrue(result["effective_blocks_match"])

    def test_removing_no_underline_does_not_hide_inherited_underline(self):
        for hyperlink in (False, True):
            with self.subTest(hyperlink=hyperlink):
                original = Document()
                paragraph = original.add_paragraph()
                run = paragraph.add_run("text")
                if hyperlink:
                    style = original.styles.add_style(
                        "UnderlinedLink", WD_STYLE_TYPE.CHARACTER
                    )
                    style.font.underline = True
                    run.style = style
                    wrapper = OxmlElement("w:hyperlink")
                    wrapper.set(
                        qn("r:id"),
                        original.part.relate_to(
                            "https://example.com", RT.HYPERLINK, is_external=True
                        ),
                    )
                    wrapper.append(run._r)
                    paragraph._p.append(wrapper)
                else:
                    original.styles["Normal"].font.underline = True
                run.underline = False
                saved = reopened(original)
                props = saved._element.xpath("//w:rPr[w:u]")[-1]
                props.remove(props.find(qn("w:u")))
                self.assertFalse(
                    self.compare(original, saved)["effective_blocks_match"]
                )

    def test_paragraph_style_font_and_font_alias_preserve_authored_font(self):
        original = MathmlToDocx().convert(
            '<math style="font-family:Malgun Gothic"><mi>x</mi></math>'
        )
        saved = reopened(original)
        for run in saved._element.xpath("//m:r"):
            props = run.find(qn("w:rPr"))
            props.remove(props.find(qn("w:rFonts")))
        normal = saved.styles["Normal"].element.get_or_add_rPr()
        fonts = OxmlElement("w:rFonts")
        for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
            fonts.set(qn("w:" + slot), "맑은 고딕")
        normal.append(fonts)
        self.assertTrue(self.compare(original, saved)["effective_blocks_match"])
        fonts.set(qn("w:ascii"), "Arial")
        self.assertFalse(self.compare(original, saved)["effective_blocks_match"])

    def test_nearest_compound_control_properties_supply_run_size(self):
        original = MathmlToDocx().convert(
            '<math style="font-size:18pt;color:red"><mfrac><mi>x</mi><mi>y</mi></mfrac></math>'
        )
        saved = reopened(original)
        for run in saved._element.xpath("//m:r"):
            props = run.find(qn("w:rPr"))
            run.remove(props)
        self.assertTrue(self.compare(original, saved)["effective_blocks_match"])

    def test_character_style_based_on_supplies_authored_properties(self):
        original = MathmlToDocx().convert(
            '<math style="font-size:18pt;color:red"><mi>x</mi></math>'
        )
        saved = reopened(original)
        parent = saved.styles.add_style("MathParent", WD_STYLE_TYPE.CHARACTER)
        parent.font.size = Pt(18)
        child = saved.styles.add_style("MathChild", WD_STYLE_TYPE.CHARACTER)
        child.base_style = parent
        child.font.color.rgb = RGBColor.from_string("FF0000")
        run = saved._element.xpath("//m:r")[0]
        run.remove(run.find(qn("w:rPr")))
        props = OxmlElement("w:rPr")
        style = OxmlElement("w:rStyle")
        style.set(qn("w:val"), "MathChild")
        props.append(style)
        run.insert(1, props)
        self.assertTrue(self.compare(original, saved)["effective_blocks_match"])
        parent.font.size = Pt(20)
        self.assertFalse(self.compare(original, saved)["effective_blocks_match"])

    def test_declared_font_table_alternate_names_are_used(self):
        original = MathmlToDocx().convert(
            '<math style="font-family:ExampleFont"><mi>x</mi></math>'
        )
        saved = reopened(original)
        for fonts in saved._element.xpath("//m:r/w:rPr/w:rFonts"):
            for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
                fonts.set(qn("w:" + slot), "LocalizedExampleFont")
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.docx", Path(tmp) / "b.docx"
            original.save(str(a))
            saved.save(str(b))
            source, output = DocxOracle(a), DocxOracle(b)
            table = ET.fromstring(output.files["word/fontTable.xml"])
            font = ET.SubElement(
                table, qn("w:font"), {qn("w:name"): "LocalizedExampleFont"}
            )
            ET.SubElement(font, qn("w:altName"), {qn("w:val"): "ExampleFont"})
            output.files["word/fontTable.xml"] = ET.tostring(table)
            self.assertTrue(
                compare_word_documents(source, output)["effective_blocks_match"]
            )

    def test_unspecified_math_font_is_not_an_authored_normal_text_font(self):
        original = MathmlToDocx().convert("<math><mi>x</mi></math>")
        original.styles["Normal"].font.name = "Malgun Gothic"
        saved = reopened(original)
        run = saved._element.xpath("//m:r")[0]
        props = OxmlElement("w:rPr")
        fonts = OxmlElement("w:rFonts")
        fonts.set(qn("w:ascii"), "Cambria Math")
        fonts.set(qn("w:hAnsi"), "Cambria Math")
        props.append(fonts)
        run.insert(1, props)
        result = self.compare(original, saved)
        self.assertTrue(result["effective_blocks_match"])
        self.assertFalse(result["raw_blocks_match"])
        self.assertTrue(result["raw_math_metadata_differences"])

    def test_symbol_script_family_mapping_preserves_weight_nor_and_mapped_symbols(self):
        for char, change, expected in (
            ("⊃", "script", True),
            ("∈", "script", True),
            ("⊃", "weight", False),
            ("+", "script", True),
            ("-", "script", True),
            ("=", "script", True),
            ("∂", "script", False),
            ("∇", "script", False),
            ("⊃", "normal", False),
            ("α", "script", False),
            ("1", "script", False),
        ):
            with self.subTest(char=char, change=change):
                tag = "mi" if char.isalpha() else "mn" if char.isdigit() else "mo"
                original = MathmlToDocx().convert(
                    "<math><" + tag + ">" + char + "</" + tag + "></math>"
                )
                saved = reopened(original)
                props = saved._element.xpath("//m:r")[0].find(qn("m:rPr"))
                if change == "normal":
                    prop = OxmlElement("m:nor")
                    prop.set(qn("m:val"), "1")
                    props.insert(0, prop)
                else:
                    prop = props.find(qn("m:scr" if change == "script" else "m:sty"))
                    prop.set(
                        qn("m:val"), "double-struck" if change == "script" else "b"
                    )
                self.assertEqual(
                    self.compare(original, saved)["effective_blocks_match"], expected
                )

    def test_authored_color_size_and_variant_changes_are_detected(self):
        original = MathmlToDocx().convert(
            '<math style="color:red;font-size:18pt"><mi mathvariant="double-struck">R</mi></math>'
        )
        for change in ("color", "size", "variant", "remove_color", "remove_size"):
            with self.subTest(change=change):
                saved = reopened(original)
                run = saved._element.xpath("//m:r")[0]
                if change == "color":
                    run.find(qn("w:rPr")).find(qn("w:color")).set(qn("w:val"), "0000FF")
                elif change == "size":
                    run.find(qn("w:rPr")).find(qn("w:sz")).set(qn("w:val"), "40")
                elif change.startswith("remove_"):
                    tag = "w:color" if change == "remove_color" else "w:sz"
                    props = run.find(qn("w:rPr"))
                    props.remove(props.find(qn(tag)))
                else:
                    run.find(qn("m:rPr")).find(qn("m:scr")).set(qn("m:val"), "roman")
                    run.find(qn("m:t")).text = "R"
                self.assertFalse(
                    self.compare(original, saved)["effective_blocks_match"]
                )

    def test_math_only_inline_wrapper_is_reported_without_hiding_inline_prose(self):
        for prose in (False, True):
            with self.subTest(prose=prose):
                original = MathmlToDocx().convert(
                    ("<p>Before " if prose else "")
                    + "<math><mi>x</mi></math>"
                    + (" after</p>" if prose else "")
                )
                saved = reopened(original)
                math = saved._element.xpath("//m:oMath")[0]
                wrapper = OxmlElement("m:oMathPara")
                math.addprevious(wrapper)
                wrapper.append(math)
                result = self.compare(original, saved)
                self.assertFalse(result["raw_blocks_match"])
                self.assertEqual(result["effective_blocks_match"], not prose)
                self.assertEqual(bool(result["serialization_differences"]), not prose)

    def test_explicit_display_alignment_changes_are_not_normalized(self):
        original = MathmlToDocx().convert(
            '<math display="block" style="text-align:right"><mi>x</mi></math>'
        )
        saved = reopened(original)
        saved._element.xpath("//m:jc")[0].set(qn("m:val"), "center")
        self.assertFalse(self.compare(original, saved)["effective_blocks_match"])

    def test_equivalent_minus_spelling_is_limited_to_math(self):
        original = MathmlToDocx().convert("<p>−<math><mo>−</mo></math></p>")
        saved = reopened(original)
        saved._element.xpath("//m:t")[0].text = "-"
        self.assertTrue(self.compare(original, saved)["effective_blocks_match"])
        saved._element.xpath("//w:t")[0].text = "-"
        self.assertFalse(self.compare(original, saved)["effective_blocks_match"])

    def test_display_math_field_and_word_hyperlink_have_identical_link_semantics(self):
        original = field_document()
        saved = reopened(original)
        math = saved._element.xpath("//m:oMath")[0]
        body = list(math)[3:-1]
        for child in list(math):
            math.remove(child)
        link = OxmlElement("w:hyperlink")
        link.set(
            qn("r:id"),
            saved.part.relate_to(
                "https://example.com/method", RT.HYPERLINK, is_external=True
            ),
        )
        link.extend(body)
        math.append(link)
        result = self.compare(original, saved)
        self.assertTrue(result["raw_blocks_match"])
        self.assertTrue(result["effective_blocks_match"])

    def test_display_math_field_url_is_not_discarded(self):
        original = field_document()
        saved = reopened(original)
        saved._element.xpath("//w:instrText")[
            0
        ].text = ' HYPERLINK "https://example.com/wrong" '
        result = self.compare(original, saved)
        self.assertFalse(result["effective_blocks_match"])
        self.assertTrue(
            any(
                change["path"].endswith("/link")
                for change in result["effective_mismatches"]
            )
        )

    def test_math_field_internal_anchor_and_split_instruction_are_checked(self):
        document = field_document()
        code = document._element.xpath("//w:instrText")[0]
        code.text = ' HYPERLINK \\l "destination" '
        run = code.getparent()
        extra = OxmlElement("m:r")
        remainder = OxmlElement("w:instrText")
        remainder.text = code.text[10:]
        code.text = code.text[:10]
        extra.append(remainder)
        run.addnext(extra)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "internal.docx"
            document.save(str(path))
            oracle = DocxOracle(path)
            item = oracle.blocks()[0]["paragraph"]["content"][0]
            self.assertEqual(item["link"], "#destination")
            self.assertTrue(item["content"][0]["display"])
            with self.assertRaisesRegex(AssertionError, "no bookmark"):
                oracle.assert_internal_links()
            start = OxmlElement("w:bookmarkStart")
            start.set(qn("w:id"), "1")
            start.set(qn("w:name"), "destination")
            end = OxmlElement("w:bookmarkEnd")
            end.set(qn("w:id"), "1")
            document.paragraphs[0]._p.insert(0, start)
            document.paragraphs[0]._p.insert(1, end)
            document.save(str(path))
            DocxOracle(path).assert_internal_links()

    def test_math_field_does_not_hide_a_changed_character_variant(self):
        original = field_document()
        source = original._element.xpath("//m:num/m:r")[0]
        source.find(qn("m:t")).text = "x"
        source.find(qn("m:rPr")).find(qn("m:sty")).set(qn("m:val"), "i")
        saved = reopened(original)
        saved._element.xpath("//m:num/m:r")[0].find(qn("m:rPr")).find(qn("m:sty")).set(
            qn("m:val"), "p"
        )
        self.assertFalse(self.compare(original, saved)["effective_blocks_match"])

    def test_redundant_field_font_flags_may_move_into_native_math_style(self):
        for style in ("p", "i", "b", "bi"):
            with self.subTest(style=style):
                original = field_document()
                source = original._element.xpath("//m:num/m:r")[0]
                source.find(qn("m:t")).text = "x"
                source.find(qn("m:rPr")).find(qn("m:sty")).set(qn("m:val"), style)
                properties = OxmlElement("w:rPr")
                for name, marker in (("b", "b"), ("i", "i")):
                    flag = OxmlElement("w:" + name)
                    flag.set(qn("w:val"), "1" if marker in style else "0")
                    properties.append(flag)
                source.insert(1, properties)
                saved = reopened(original)
                run = saved._element.xpath("//m:num/m:r")[0]
                run.remove(run.find(qn("w:rPr")))
                result = self.compare(original, saved)
                self.assertTrue(result["effective_blocks_match"])
                self.assertFalse(result["raw_blocks_match"])
                contradiction = OxmlElement("w:rPr")
                flag = OxmlElement("w:i")
                flag.set(qn("w:val"), "0" if "i" in style else "1")
                contradiction.append(flag)
                run.insert(1, contradiction)
                self.assertFalse(
                    self.compare(original, saved)["effective_blocks_match"]
                )

    def test_field_target_escaping_preserves_the_declared_url(self):
        target = 'https://example.com/a\\b?title="ratio"'
        document = field_document()
        escaped = target.replace("\\", "\\\\").replace('"', '\\"')
        document._element.xpath("//w:instrText")[0].text = (
            ' HYPERLINK "' + escaped + '" '
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "escaped.docx"
            document.save(str(path))
            oracle = DocxOracle(path)
            self.assertEqual(
                oracle.blocks()[0]["paragraph"]["content"][0]["link"], target
            )

    def test_malformed_unknown_and_nested_math_fields_are_rejected(self):
        for change in ("missing_end", "missing_separate", "unknown_code", "nested"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                document = field_document()
                math = document._element.xpath("//m:oMath")[0]
                if change == "missing_end":
                    math.remove(math[-1])
                elif change == "missing_separate":
                    math.remove(math[2])
                elif change == "unknown_code":
                    document._element.xpath("//w:instrText")[
                        0
                    ].text = ' INCLUDETEXT "file:///private" '
                else:
                    math.insert(
                        3, reopened(field_document())._element.xpath("//m:oMath")[0][0]
                    )
                path = Path(tmp) / "malformed.docx"
                document.save(str(path))
                oracle = DocxOracle(path)
                for accessor in (
                    oracle.equations,
                    oracle.blocks,
                    lambda oracle=oracle: oracle.math_runs(0),
                ):
                    with self.assertRaises(AssertionError):
                        accessor()


if __name__ == "__main__":
    unittest.main()
