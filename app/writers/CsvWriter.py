import logging, csv, os
import settings

class CsvWriter:
    def __init__(self) -> None:
        self.logger = logging.getLogger('CSVWriter')
    
    def start(self, filename):
        file = open(os.path.join(settings.OUTPUT_DIR, filename.replace('.csv', '_output.csv')), 'w', encoding='utf-8', newline='')
        
        self.logger.info('Writing output to %s', file.name)
        
        self.writer = csv.writer(file)
        self.file = file
        
    def finish(self):
        if self.file:
            self.file.close()
            
    def writeline(self, line):
        self.writer.writerow(line)
        