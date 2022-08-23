import csv, os, logging, sys, argparse
from logging.handlers import RotatingFileHandler
import settings
from parts_parser import parse_part
from writers.CsvWriter import CsvWriter
from writers.XlsxWriter import XlsxWriter
        
WRITERS = {
    'csv': CsvWriter,
    'xlsx': XlsxWriter
}        

class Scraper:
    writers = []
    
    def __init__(self, writers = ''):
        self.logger = logging.getLogger('Scraper')
        
        for name in writers.split(','):
            if name in WRITERS:
                self.writers.append(WRITERS[name]())
                self.logger.info('Created %s writer', name)
            else:
                self.logger.info('%s writer is not declared', name)
    
    def read(self, path):
        logger = self.logger
        
        if len(self.writers) == 0:
            logger.warning('No writers registered, quitting')
            return
        
        logger.info('Processing %s', path)
        
        # iterate the writing pipeline objects and let them know we're reading new file
        for writer in self.writers:
            writer.start(path)
    
        with open(os.path.join(settings.INPUT_DIR, path), newline='') as input:
            reader = csv.reader(input)
            
            # write header
            self.write(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
            
            for line in reader:
                logger.info('Processing part {} {}'.format(*line))
                
                for l in parse_part(*line):
                    self.write(l)
                    
        # iterate the writing pipeline objects and let them know file is processed
        for writer in self.writers:
            writer.finish()
    
    def write(self, line):
        for writer in self.writers:
            writer.writeline(line)
            
    def run(self):
        self.logger.info('Parser started')
        
        for file in os.listdir(settings.INPUT_DIR):
            if file[-3:] == 'csv':
                self.read(file)
                
        self.logger.info('Parser finished')


def start(output):
    scraper = Scraper(writers=output)

    scraper.run()


def setup_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)

    if not isinstance(numeric_level, int):
        print('Invalid log level: %s' % loglevel)
        sys.exit(1)

    rotateHandler = RotatingFileHandler(
        filename='../log/parser.log',
        # 10 MB
        maxBytes=1024 * 1024 * 10,
        backupCount=3
    )

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=numeric_level,
        handlers=[rotateHandler]
    )


def main(argv):
    loglevel = 'ERROR'
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', dest='loglevel', choices=('info', 'warning', 'error'), default='warning', help='Set log level')
    parser.add_argument('--output', dest='output', default='csv', help='Comma-separated list of writers (csv and xlsx supported)')
    
    args = parser.parse_args()
    
    loglevel = args.loglevel
    
    setup_logging(loglevel)
    
    try:
        start(args.output)
    except BaseException as e:
        logging.critical(e)


if __name__ == '__main__':
    main(sys.argv[1:])
