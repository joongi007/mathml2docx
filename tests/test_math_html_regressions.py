"""MathML keeps document structure, destinations and supported CSS."""

from docx import Document
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx, mathml_to_omml

NS = {
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def test_block_math_occupies_cell_before_following_text():
    document = Document()
    cell = document.add_table(rows=1, cols=1).cell(0, 0)
    MathmlToDocx().add_html_to_cell(
        '<math display="block"><mi>x</mi></math><p>after</p>', cell
    )
    assert len(cell.paragraphs) == 2
    assert cell.paragraphs[0]._p.xpath("./m:oMathPara")
    assert cell.paragraphs[1].text == "after"


def test_math_inherits_html_styles_and_descendant_stylesheet_rules():
    document = MathmlToDocx().convert("""
        <style>math .answer {color:blue;font-size:150%;font-family:"Courier New"}</style>
        <div style="color:red;font-size:20pt;font-family:Arial">
          <math><mi>x</mi><mi class="answer">y</mi></math>
        </div>""")
    runs = document._element.xpath("//m:r")
    assert runs[0].xpath("./w:rPr/w:color/@w:val", namespaces=NS) == ["FF0000"]
    assert runs[0].xpath("./w:rPr/w:sz/@w:val", namespaces=NS) == ["40"]
    assert runs[0].xpath("./w:rPr/w:rFonts/@w:eastAsia", namespaces=NS) == ["Arial"]
    assert runs[1].xpath("./w:rPr/w:color/@w:val", namespaces=NS) == ["0000FF"]
    assert runs[1].xpath("./w:rPr/w:sz/@w:val", namespaces=NS) == ["60"]
    assert runs[1].xpath("./w:rPr/w:rFonts/@w:cs", namespaces=NS) == ["Courier New"]


def test_native_math_style_inherits_and_styles_compound_controls():
    root = mathml_to_omml("""<math mathcolor="red" mathsize="18pt"
        style="font-family:Arial"><mfrac><mi>x</mi>
        <mstyle mathcolor="blue"><mi>y</mi></mstyle></mfrac></math>""")
    ns = {
        "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }
    assert root.xpath(".//m:fPr/m:ctrlPr/w:rPr/w:color/@w:val", namespaces=ns) == [
        "FF0000"
    ]
    assert root.xpath(".//m:r/w:rPr/w:color/@w:val", namespaces=ns) == [
        "FF0000",
        "0000FF",
    ]
    assert root.xpath(".//m:r/w:rPr/w:sz/@w:val", namespaces=ns) == ["36", "36"]


def test_root_math_attributes_resolve_against_html_inheritance():
    document = MathmlToDocx().convert(
        '<div style="color:red;font-size:20pt">'
        '<math mathcolor="currentColor" mathsize="200%"><mi>x</mi></math></div>'
    )
    assert document._element.xpath("//m:r/w:rPr/w:color/@w:val") == ["FF0000"]
    assert document._element.xpath("//m:r/w:rPr/w:sz/@w:val") == ["80"]


def test_math_color_alpha_uses_surrounding_background():
    document = MathmlToDocx().convert(
        '<div style="background-color:blue;color:rgba(255,0,0,0.5)">A'
        '<math><mi>x</mi><mi style="color:rgba(0,255,0,0.5)">y</mi></math></div>'
    )
    assert document._element.xpath("//w:r/w:rPr/w:color/@w:val") == ["800080"]
    assert document._element.xpath("//m:r/w:rPr/w:color/@w:val") == ["800080", "008080"]
    document = MathmlToDocx().convert(
        '<div style="background-color:blue">'
        '<math style="background-color:rgba(255,0,0,0.5);color:rgba(0,255,0,0.5)">'
        "<mi>x</mi></math></div>"
    )
    assert document._element.xpath("//m:r/w:rPr/w:color/@w:val") == ["408040"]


def test_styles_false_ignores_css_within_and_outside_math():
    document = MathmlToDocx(styles=False).convert("""<div style="color:red">
        <math style="font-size:30pt"><mi style="color:blue">x</mi></math></div>""")
    assert not document._element.xpath("//m:r/w:rPr")


def test_styles_false_recovery_still_receives_complete_source():
    import warnings

    source = '<math style="color:red"><unknown/></math>'
    seen = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        MathmlToDocx(
            styles=False, mathml_fallback=lambda s, e: seen.append(s) or s
        ).parse_mathml(source)
    assert seen == [source]


def test_math_id_is_a_bookmark_and_internal_link_destination():
    document = MathmlToDocx().convert("""<p><a href="#equation">See equation</a></p>
        <math id="equation" display="block"><mi>x</mi></math>""")
    assert document._element.xpath("//w:hyperlink/@w:anchor") == ["equation"]
    starts = document._element.xpath('//w:bookmarkStart[@w:name="equation"]')
    assert len(starts) == 1
    assert starts[0].getparent().xpath("./m:oMathPara")
    assert document._element.xpath("//w:bookmarkEnd/@w:id") == [
        starts[0].get(qn("w:id"))
    ]


def test_hyperlink_scope_survives_display_math_and_following_paragraphs():
    document = MathmlToDocx().convert("""<p>Before <a href="https://example.com">
        first<math display="block"><mi>x</mi></math>last</a> after</p>""")
    assert len(document.paragraphs) == 3
    assert document.paragraphs[0]._p.xpath("./w:hyperlink//w:t/text()") == ["first"]
    assert document.paragraphs[1]._p.xpath("./m:oMathPara//m:t/text()") == ["x"]
    assert not document.paragraphs[1]._p.xpath("./w:hyperlink")
    assert document.paragraphs[1]._p.xpath(
        "./m:oMathPara/m:oMath/m:r/w:instrText/text()"
    ) == [' HYPERLINK "https://example.com" ']
    assert document.paragraphs[1]._p.xpath(
        "./m:oMathPara/m:oMath/m:r/w:fldChar/@w:fldCharType"
    ) == ["begin", "separate", "end"]
    assert document.paragraphs[2]._p.xpath("./w:hyperlink//w:t/text()") == ["last"]
    assert document.paragraphs[2]._p.xpath("./w:r/w:t/text()") == [" after"]
    assert len(set(document._element.xpath("//w:hyperlink/@r:id"))) == 1


def test_display_math_link_keeps_mixed_styles_and_existing_run_fonts():
    document = MathmlToDocx().convert(
        '<a href="https://example.com"><math display="block" style="color:red;font-size:18pt;font-family:Arial">'
        '<mi>x</mi><mi mathvariant="normal">N</mi><mi mathvariant="bold">z</mi><mtext>label</mtext>'
        "</math></a>"
    )
    assert len(document._element.xpath("//m:oMath")) == 1
    runs = document._element.xpath("//m:r[m:t]")
    assert [r.find("w:rPr/w:i", NS).get(qn("w:val"), "1") for r in runs] == [
        "1",
        "0",
        "0",
        "0",
    ]
    assert [r.find("w:rPr/w:b", NS).get(qn("w:val"), "1") for r in runs] == [
        "0",
        "0",
        "1",
        "0",
    ]
    for run in runs:
        assert run.xpath("./w:rPr/w:color/@w:val", namespaces=NS) == ["FF0000"]
        assert run.xpath("./w:rPr/w:sz/@w:val", namespaces=NS) == ["36"]
        assert run.xpath("./w:rPr/w:rFonts/@w:ascii", namespaces=NS) == ["Arial"]


def test_display_math_link_quotes_external_target_and_internal_bookmark():
    document = MathmlToDocx().convert(
        '<a href="https://example.com/a&quot;b\\c"><math display="block"><mi>x</mi></math></a>'
        '<a href="#result"><math display="block"><mi>y</mi></math></a>'
        '<p id="result">Target</p>'
    )
    assert document._element.xpath("//m:r/w:instrText/text()") == [
        ' HYPERLINK "https://example.com/a\\"b\\\\c" ',
        ' HYPERLINK \\l "result" ',
    ]
    assert document._element.xpath("//w:bookmarkStart/@w:name") == ["result"]


def test_display_math_link_rejects_control_characters_in_target():
    import pytest

    with pytest.raises(ValueError, match="control"):
        MathmlToDocx().convert(
            '<a href="https://example.com/&#10;bad"><math display="block"><mi>x</mi></math></a>'
        )


def test_prefixed_xml_math_in_html_is_explicitly_rejected():
    import pytest

    with pytest.raises(ValueError, match="parse_mathml"):
        MathmlToDocx().convert("""<p><m:math xmlns:m="http://www.w3.org/1998/Math/MathML">
            <m:mi>x</m:mi></m:math></p>""")


def test_hyperlink_containing_paragraphs_has_no_empty_leading_paragraph():
    document = MathmlToDocx().convert(
        '<a href="https://example.com"><p>first</p><p>last</p></a>'
    )
    assert len(document.paragraphs) == 2
    assert document._element.xpath("//w:hyperlink//w:t/text()") == ["first", "last"]


def test_math_paragraph_properties_do_not_extend_hyperlink_to_previous_text():
    document = MathmlToDocx().convert(
        '<p>Before <a href="https://example.com" style="text-align:right">'
        "<math><mi>x</mi></math></a> after</p>"
    )
    assert document.paragraphs[0]._p.xpath("./w:r/w:t/text()") == ["Before ", " after"]
    assert document.paragraphs[0]._p.xpath("./w:hyperlink//m:t/text()") == ["x"]


def test_standalone_math_honors_inline_display_css():
    document = MathmlToDocx().parse_mathml(
        '<math style="display:block"><mi>x</mi></math>'
    )
    assert document._element.xpath("//m:oMathPara")
