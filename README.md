# mathml2docx
The fork in [htmldocx](https://github.com/pqzx/html2docx) converts html (including mathml) to docx     
Dependencies: `python-docx` & `bs4`

### To install

`pip install mathml2docx`

### Imporvements
- Add: Convert mathml to docx formula
- Add: MathmlToDocx, a wrapper class for InteliSense and encapsulation
- Add: Etc...
- Fix: Known errors in the original repository

### Usage

Add strings of html to an existing docx.Document object

```
from docx import Document
from mathml2docx import MathmlToDocx

document = Document()
new_parser = MathmlToDocx()
# do stuff to document

html = '<h1>Hello world</h1>'
new_parser.add_html_to_document(html, document)

# do more stuff to document
document.save('your_file_name')
```

Convert files directly

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.parse_html_file(input_html_file_path, output_docx_file_path)
```

Convert files from a string

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
docx = new_parser.parse_html_string(input_html_file_string)
```

Change table styles

Tables are not styled by default. Use the `table_style` attribute on the parser to set a table
style. The style is used for all tables.

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.table_style = 'Light Shading Accent 4'
```

To add borders to tables, use the `TableGrid` style:

```
new_parser.table_style = 'TableGrid'
```

Default table styles can be found
here: https://python-docx.readthedocs.io/en/latest/user/styles-understanding.html#table-styles-in-default-template

Change default paragraph style

No style is applied to the paragraphs by default. Use the `paragraph_style` attribute on the parser
to set a default paragraph style. The style is used for all paragraphs. If additional styling (
color, background color, alignment...) is defined in the HTML, it will be applied after the
paragraph style.

```
from mathml2docx import MathmlToDocx

new_parser = MathmlToDocx()
new_parser.paragraph_style = 'Quote'
```

Default paragraph styles can be found
here: https://python-docx.readthedocs.io/en/latest/user/styles-understanding.html#paragraph-styles-in-default-template
