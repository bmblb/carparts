import csv
from bs4 import BeautifulSoup
import json
import re
from site_parsers.parser_emex.parser import get_data_from_json as emex_get_data


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
    
def exist_test():
    with open('../output/test.csv', 'w') as file:
        writer = csv.writer(file)
        
        writer.writerows([[1,2,3], [1,2,3]])
        
def emex_test():
    with open('./site_parsers/parser_emex/resources/response.json') as input:
        result = emex_get_data(json.loads(input.read()))
        
        with open('../output/emex_test.csv', 'w') as out:
            writer = csv.writer(out)
        
            writer.writerow(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])    
            writer.writerows(result)

def main():
    # exist_test()
    emex_test()
    

if __name__ == '__main__':
    main()
    