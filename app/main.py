import csv, os, logging, sys, argparse
from logging.handlers import RotatingFileHandler
import settings
from parts_parser import parse_part

def read(path):
    logging.info('Processing %s', path)
    
    with open(os.path.join(settings.INPUT_DIR, path), newline='') as input:
        reader = csv.reader(input)
        
        with open(os.path.join(settings.OUTPUT_DIR, path.replace('.csv', '_output.csv')), 'w') as out:
            logging.info('Writing output to %s', out.name)
            
            writer = csv.writer(out)
            
            # write header
            writer.writerow(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
            
            for line in reader:
                logging.info('Processing part {} {}'.format(*line))
                
                for l in parse_part(*line):
                    writer.writerow(l)


def start():
    logging.info('Parser started')
    for file in os.listdir(settings.INPUT_DIR):
        if file[-3:] == 'csv':
            read(file)


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
    parser.add_argument('--loglevel', dest='loglevel', choices=('info', 'warning', 'error'), default='info', help='Set log level')
    
    args = parser.parse_args()
    
    loglevel = args.loglevel

    setup_logging(loglevel)
    
    start()
    # try:
    #     start()
    # except BaseException as e:
    #     logging.critical(e)


if __name__ == '__main__':
    main(sys.argv[1:])
