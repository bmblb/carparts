import csv, os
import imp
import settings
from parts_parser import parse

def read(path):
    with open(path, newline='') as file:
        reader = csv.reader(file)
        line = reader.__next__()
        print(line)
        parse(line[0], line[1])
        # for row in reader:
        #     print(row)
            
def main():
    for file in os.listdir(settings.INPUT_DIR):
        if file[-3:] == 'csv':
            read(os.path.join(settings.INPUT_DIR, file))

if __name__ == '__main__':
    main()
