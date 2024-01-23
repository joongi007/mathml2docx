import argparse
from io import BytesIO
from typing import Union
from docx.document import Document
from docx.table import _Cell

from .h2d import HtmlToDocx, DEFAULT_TABLE_STYLE, DEFAULT_PARAGRAPH_STYLE

class MathmlToDocx:
    def __init__(self, 
                 fix_html = True, 
                 images = True, 
                 tables = True, 
                 mathml = True, 
                 styles = True, 
                 table_style = DEFAULT_TABLE_STYLE, 
                 paragraph_style = DEFAULT_PARAGRAPH_STYLE):
        self.__h2d = HtmlToDocx()
        self.__options = MathmlTODocxOption(self.__h2d, fix_html, images, tables, mathml, styles)
        self.__h2d.table_style = table_style
        self.__h2d.paragraph_style = paragraph_style

    def get_origin(self) -> HtmlToDocx:
        return self.__h2d
    
    @property
    def options(self) -> "MathmlTODocxOption":
        return self.__options

    @property
    def table_style(self) -> Union[str, None]:
        return self.__h2d.table_style

    @table_style.setter
    def table_style(self, table_style : Union[str, None]):
        self.__h2d.table_style = table_style

    @property
    def paragraph_style(self) -> Union[str, None]:
        return self.__h2d.paragraph_style

    @paragraph_style.setter
    def paragraph_style(self, paragraph_style : Union[str, None]):
        self.__h2d.paragraph_style = paragraph_style

    def copy_settings_from(self, other : Union["MathmlToDocx", HtmlToDocx]):
        if isinstance(other, MathmlToDocx):
            self.__h2d.copy_settings_from(other.get_origin())
        elif isinstance(other, HtmlToDocx):
            self.__h2d.copy_settings_from(other)
        else:
            raise TypeError(f"'other' expect either Type {MathmlToDocx} or Type {HtmlToDocx}, but not Type {type(other)}.")

    def add_image_to_cell(self, cell : Union[Document, _Cell], image : BytesIO):
        if not isinstance(cell, _Cell) and not isinstance(cell, Document):
            raise TypeError(f"'cell' expect either Type {_Cell} or Type {Document}, but not Type {type(cell)}.")
        if not isinstance(image, BytesIO):
            raise TypeError(f"'image' expect either Type {BytesIO}, but not Type {type(image)}.")
        self.__h2d.add_image_to_cell(cell, image)

    def add_html_to_document(self, html : str, document : Union[Document, _Cell]):
        if not type(html) is str:
            raise TypeError(f"'html' expect either Type {str}, but not Type {type(html)}.")
        if not isinstance(document, Document) and not isinstance(document, _Cell):
            raise TypeError(f"'document' expect either Type {Document} or {_Cell}, but not Type {type(document)}.")
        self.__h2d.add_html_to_document(html, document)

    def add_html_to_cell(self, html : str, cell : _Cell):
        if not type(html) is str:
            raise TypeError(f"'html' expect either Type {str}, but not Type {type(html)}.")
        if not isinstance(cell, _Cell):
            raise TypeError(f"'document' expect either Type {_Cell}, but not Type {type(cell)}.")
        self.__h2d.add_html_to_cell(html, cell)

    def parse_html_file(self, filename_html : str, filename_docx:Union[str, None]=None, encoding:str='utf-8'):
        if not type(filename_html) is str:
            raise TypeError(f"'filename_html' expect either Type {str}, but not Type {type(filename_html)}.")
        if filename_docx and not type(filename_docx) is str:
            raise TypeError(f"'filename_docx' expect either Type {str} or  Type {None}, but not Type {type(filename_docx)}.")
        if not type(encoding) is str:
            raise TypeError(f"'encoding' expect either Type {str}, but not Type {type(encoding)}.")
        self.__h2d.parse_html_file(filename_html, filename_docx, encoding)
    
    def parse_html_string(self, html : str) -> Document:
        if not type(html) is str:
            raise TypeError(f"'html' expect either Type {str}, but not Type {type(html)}.")
        return self.__h2d.parse_html_string(html)
    
    def add_styles_to_paragraph(self, style : str):
        if not type(style) is str:
            raise TypeError(f"'style' expect either Type {str}, but not Type {type(style)}.")
        self.__h2d.add_styles_to_paragraph(style)

    def add_styles_to_run(self, style : str):
        if not type(style) is str:
            raise TypeError(f"'style' expect either Type {str}, but not Type {type(style)}.")
        self.__h2d.add_styles_to_run(style)

class MathmlTODocxOption:
    def __init__(self, h2d, fix_html, images, tables, mathml, styles):
        # init
        self.__h2d = h2d
        self.__fix_html = fix_html
        self.__images = images
        self.__tables = tables
        self.__mathml = mathml
        self.__styles = styles

        # h2d options init
        self.__h2d.options["fix-html"] = self.__fix_html
        self.__h2d.options["images"] = self.__images
        self.__h2d.options["tables"] = self.__tables
        self.__h2d.options["mathml"] = self.__mathml
        self.__h2d.options["styles"] = self.__styles

    @property
    def fix_html(self) -> bool:
        self.__fix_html = self.__h2d.options["fix-html"]
        return self.__fix_html

    @fix_html.setter
    def fix_html(self, fix_html : bool):
        self.__fix_html = fix_html
        self.__h2d.options["fix-html"] = fix_html

    @property
    def images(self) -> bool:
        self.__images = self.__h2d.options["images"]
        return self.__images

    @images.setter
    def images(self, images : bool):
        self.__images = images
        self.__h2d.options["images"] = images

    @property
    def tables(self) -> bool:
        self.__tables =  self.__h2d.options["tables"]
        return self.__tables

    @tables.setter
    def tables(self, tables : bool):
        self.__tables = tables
        self.__h2d.options["tables"] = tables

    @property
    def mathml(self) -> bool:
        self.__mathml = self.__h2d.options["mathml"]
        return self.__mathml

    @mathml.setter
    def mathml(self, mathml : bool):
        self.__mathml = mathml
        self.__h2d.options["mathml"] = mathml

    @property
    def styles(self) -> bool:
        self.__styles = self.__h2d.options["styles"]
        return self.__styles

    @styles.setter
    def styles(self, styles : bool):
        self.__styles = styles
        self.__h2d.options["styles"] = styles

if __name__=='__main__':
    arg_parser = argparse.ArgumentParser(description='Convert .html file into .docx file with formatting')
    arg_parser.add_argument('filename_html', help='The .html file to be parsed')
    arg_parser.add_argument(
        'filename_docx', 
        nargs='?', 
        help='The name of the .docx file to be saved. Default new_docx_file_[filename_html]', 
        default=None
    )
    arg_parser.add_argument('--bs', action='store_true', 
        help='Attempt to fix html before parsing. Requires bs4. Default True')

    args = vars(arg_parser.parse_args())
    file_html = args.pop('filename_html')
    html_parser = MathmlToDocx()
    html_parser.parse_html_file(file_html, **args)