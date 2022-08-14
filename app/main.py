import csv, os, logging
import settings
from parts_parser import parse_part

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def read(path):
    with open(os.path.join(settings.INPUT_DIR, path), newline='') as input:
        reader = csv.reader(input)
        
        with open(os.path.join(settings.OUTPUT_DIR, path.replace('.csv', '_output.csv')), 'w') as out:
            writer = csv.writer(out)
            
            # write header
            writer.writerow(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
            
            for line in reader:
                print(line)
                for l in parse_part(*line):
                    writer.writerow(l)
            
def main():
    for file in os.listdir(settings.INPUT_DIR):
        if file[-3:] == 'csv':
            read(file)

if __name__ == '__main__':
    main()
