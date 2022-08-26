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

def print_percent_done(index, total, bar_len=50, title='Please wait'):
    '''
    index is expected to be 0 based index. 
    0 <= index < total
    '''
    percent_done = (index+1)/total*100
    percent_done = round(percent_done, 1)

    done = round(percent_done/(100/bar_len))
    togo = bar_len-done

    done_str = '█'*int(done)
    togo_str = '░'*int(togo)

    print(' ' * 80, end='\r')

    print(f'[{done_str}{togo_str}] {percent_done/100:.2%} {title}', end='\r')

    if round(percent_done) == 100:
        print(' ' * 80, end='\r')


class Scraper:
    writers = []
    
    def __init__(self, writers = '', delay = 60):
        self.logger = logging.getLogger('Scraper')
        self.delay = delay
        
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
            
        filename = os.path.join(settings.INPUT_DIR, path)
        
        lines = sum(1 for _ in open(filename)) + 1
    
        with open(filename, newline='') as input:
            reader = csv.reader(input)
            
            # write header
            self.write(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
            
            i = 0
            
            for line in reader:
                if i == 0:
                    print_percent_done(0, lines, title='{} {}'.format(*line))
                
                logger.info('Processing part {} {}'.format(*line))
                
                i = i + 1
                
                for l in parse_part(*line, self.delay):
                    self.write(l)
                    
                print_percent_done(i, lines, title='{} {}'.format(*line))
                    
        # iterate the writing pipeline objects and let them know file is processed
        for writer in self.writers:
            writer.finish()
            
        print_percent_done(100, 100, title='Done')
        print('')
    
    def write(self, line):
        for writer in self.writers:
            writer.writeline(line)
            
    def run(self):
        self.logger.info('Parser started')
        
        for file in os.listdir(settings.INPUT_DIR):
            if file[-3:] == 'csv':
                self.read(file)
                
        self.logger.info('Parser finished')


def start(output, delay):
    scraper = Scraper(writers=output, delay=delay)

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
        backupCount=3,
        encoding='utf-8'
    )

    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=numeric_level,
        handlers=[rotateHandler]
    )


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', dest='loglevel', choices=('info', 'warning', 'error'), default='warning', help='Set log level')
    parser.add_argument('--output', dest='output', default='csv', help='Comma-separated list of writers (csv and xlsx supported)')
    parser.add_argument('--delay', dest='delay', type=int, default=60, help='Delay in seconds between requests')
    
    args = parser.parse_args()
    
    setup_logging(args.loglevel)
    
    try:
        start(args.output, args.delay)
    except BaseException as e:
        logging.exception(e)


if __name__ == '__main__':
    main(sys.argv[1:])
