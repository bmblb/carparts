import csv, os
import settings
from parts_parser import parse_part

def read(path):
    print(path)
    
    with open(os.path.join(settings.INPUT_DIR, path), newline='') as input:
        reader = csv.reader(input)
        
        # container for output for each part
        result = []
        
        for line in reader:
            print(line)
            result = result + parse_part(line[0], line[1])
            
        with open(os.path.join(settings.OUTPUT_DIR, path.replace('.csv', '_output.csv')), 'w') as out:
            writer = csv.writer(out)
            
            writer.writerows(result)
            
def main():
    for file in os.listdir(settings.INPUT_DIR):
        if file[-3:] == 'csv':
            read(file)

if __name__ == '__main__':
    main()
