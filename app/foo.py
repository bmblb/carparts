import csv
from bs4 import BeautifulSoup
import json
import re


def check_content():
    with open('tmp.html') as file:
        soup = BeautifulSoup(file.read(), features='html.parser')
        
        form = soup.find(attrs={'id':'form1'})
        
        script = form.find('script')
        
        # print(script.contents[0])
        
        contents = re.search(r'(\[{.+?(}\]));', script.contents[0])
        print(contents.group(1))
        
        # json_data = contents.group(0)[0:-1]
        # # print(json_data)
        # data = json.loads(json_data)
        # print(data[0])
    
def csv_test():
    with open('../output/test.csv', 'w') as file:
        writer = csv.writer(file)
        
        writer.writerows([[1,2,3], [1,2,3]])

def main():
    csv_test()
    

if __name__ == '__main__':
    main()
    