import os
import pathlib
import xlsxwriter


class SpreadSheetWriter:
    properties = {'title', 'subject', 'author', 'manager', 'company',
                   'category', 'keywords', 'comments', 'status'}
    
    def __init__(self, path: str):
        p = pathlib.Path(path)
        if p.parent.exists():
            self._path = path
        else:
            self._path = os.path.normpath('{0}/{1}'.format(os.getcwd(), path))
        self._workbook = xlsxwriter.Workbook(self._path)
        self._worksheet = self._workbook.add_worksheet()        # [sheet name]
            
    def __repr__(self) -> str:
        return '{0}({1})'.format(type(self).__name__, self._path)
    
    def __enter__(self):
        """ Allows SpreadSheetWriter to be used with a context manager.
            Automatically saves and writes the spreadsheet upon exit, even if an exception is raised.
        """
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        self.save()
        
    @property
    def worksheet(self) -> xlsxwriter.worksheet.Worksheet:
        """ Return the current worksheet """
        return self._worksheet
    
    @property
    def workbook(self) -> xlsxwriter.workbook.Workbook:
        """ Return the workbook """
        return self._workbook
    
    def save(self):
        """ Save, write, and close the file """
        try:
            self._workbook.close()
            
        except PermissionError as e:
            message = '{0};\n  If the spreadsheet is open in a viewer (e.g., Excel), try closing it first and then call save() again.'.format(str(e))
            raise PermissionError(message)
           
        
    def set_properties(self, **properties) -> None:
        """ Set spreadsheet properties to those denotes in dict properties.
            Reference class method SpreadSheetWriter.properties() for valid properties.
        """
        for prop in properties:
            if prop not in SpreadSheetWriter.properties:
                raise ValueError('property {0} is not a valid property; valid properties include:\n  {1}'.format(prop, SpreadSheetWriter.properties))

        self._workbook.set_properties(properties)
        
        
    def set_column(self, first_col: int, last_col=None, width=10, cell_format=None, **options) -> None:
        """ Sets columns first_col through last_col with the corresponding attributes.
            If last_col=None, then sets first_col only.
        """
        if last_col is None:
            last_col = first_col
        self._worksheet.set_column(first_col, last_col, width=width, cell_format=cell_format, options=options)
    
    
    def format(self, bold=False, underline=False, italics=False, 
               font_size=11, font_color='black', 
               align='left', vertical_align='vcenter', 
               border=1, wrap_text=True, **additional) -> xlsxwriter.format.Format:
        """ Return a Format object with the denoted attributes.
            Helper method for modifying actions.
        """
        options = {'bold': bold, 'underline': underline, 'italic': italics,
                   'font_size': font_size, 'align': align, 'valign': vertical_align,
                   'border': border, 'text_wrap': wrap_text, 'font_color': font_color}
        options.update(additional)
        return self._workbook.add_format(options)
    
    
    def span_row(self, row: int, col: int, depth: int, text: str, cell_format=None) -> None:
        """ Writes text and spans cell at (row, col) 'depth' rows down """
        self._worksheet.merge_range(row, col, row + depth - 1, col, text, cell_format)
        
        
    def span_col(self, row: int, col: int, distance: int, text: str, cell_format=None) -> None:
        """ Writes text and spans cell at (row, col) across 'distance' columns to the right """
        self._worksheet.merge_range(row, col, row, col + distance - 1, text, cell_format)
        
        
    def write(self, row: int, col: int, text: str, 
              bold=False, underline=False, italics=False,
              border=1, align='left', vertical_align='vcenter', 
              wrap_text=True, color='black', **kwargs) -> None:
        """ Write text to cell located at (row, col).
            Specify default options:
            align options: ('center', 'right', 'fill', 'justify', 'center_across')
            vertical_align options: ('top', 'vcenter', 'bottom', 'vjustify')
            **kwargs allows for other options that are default arguments of this method.
        """
        fmt = self.format(bold=bold, underline=underline, italics=italics, 
                          border=border, align=align, vertical_align=vertical_align, 
                          wrap_text=wrap_text, font_color=color, **kwargs)
        self._worksheet.write(row, col, text, fmt)
    def write_url(self, row: int, col: int, url: str, String=None, tip=None,
              bold=False, underline=False, italics=False,
              border=1, align='left', vertical_align='vcenter', 
              wrap_text=True, color='black', **kwargs) -> None:
        """ Write text to cell located at (row, col).
            Specify default options:
            align options: ('center', 'right', 'fill', 'justify', 'center_across')
            vertical_align options: ('top', 'vcenter', 'bottom', 'vjustify')
            **kwargs allows for other options that are default arguments of this method.
        """
        fmt = self.format(bold=bold, underline=underline, italics=italics, 
                          border=border, align=align, vertical_align=vertical_align, 
                          wrap_text=wrap_text, font_color=color, **kwargs)
        self._worksheet.write_url(row, col, url, fmt, String, tip)
        


    
if __name__ == '__main__':
    pass

