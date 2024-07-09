import os
from .context import MathmlToDocx, test_dir

# Manual test (requires inspection of result) for converting code and pre blocks.

filename = os.path.join(test_dir, 'dataset', 'code.html')
d = MathmlToDocx()

d.parse_html_file(filename)
