import logging, os
import xlsxwriter
import settings

class XlsxWriter:
    def __init__(self) -> None:
        self.logger = logging.getLogger('XSLXWriter')
        
    def start(self, filename):
        name = filename.replace('.csv', '_output.xlsx')
        
        workbook = xlsxwriter.Workbook(os.path.join(settings.OUTPUT_DIR, name))
        worksheet = workbook.add_worksheet(filename)
        
        self.logger.info('Writing output to %s', name)
        
        self.workbook = workbook
        self.worksheet = worksheet
        self.current_row = 0
        
    def finish(self):
        self.current_row = 0
        
        if self.workbook:
            self.workbook.close()
            
    def writeline(self, line):
        self.worksheet.write_row(self.current_row, 0, line)
        self.current_row += 1
        
        