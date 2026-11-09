"""18 options example."""

from mathml2docx import MathmlToDocx

from .support import save

source = MathmlToDocx(images=False, tables=False, mathml=False)
parser = MathmlToDocx()
parser.copy_settings_from(source)
parser.options.styles = False
assert parser.get_origin() is parser
html = '<h1>Options</h1><p><b>Plain</b><img src="missing"></p><table><tr><td>Skipped</td></tr></table><math><mi>x</mi></math>'
save(parser.parse_html_string(html), "18_options.docx")
