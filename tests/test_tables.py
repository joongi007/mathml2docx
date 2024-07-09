import os
from .context import MathmlToDocx, test_dir

# Manual test (requires inspection of result) for converting html with nested tables

filename = os.path.join(test_dir, 'dataset', 'tables2.html')
d = MathmlToDocx()

d.parse_html_file(filename)
