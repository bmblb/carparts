import csv, json, re, sys
from bs4 import BeautifulSoup
import xlsxwriter
from writers.XlsxWriter import XlsxWriter
from time import sleep
import requests

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
        
# def emex_test():
#     with open('./site_parsers/parser_emex/resources/response.json') as input:
#         result = emex_get_data(json.loads(input.read()))
        
#         with open('../output/emex_test.csv', 'w') as out:
#             writer = csv.writer(out)
        
#             writer.writerow(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])    
#             writer.writerows(result)


def xls_test():
    workbook = xlsxwriter.Workbook('test.xlsx')
    worksheet = workbook.add_worksheet()
    
    worksheet.write_row(0, 0, ['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
    
    workbook.close()
    
def writer_test():
    writer = XlsxWriter()
    
    writer.start('foo.csv')
    
    writer.writeline(['code', 'id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration'])
    writer.writeline(['100', '1', 'toyota', '123', 4.3, 'foo', 50, 1900.15, '10-12', '3 days'])
    
    writer.finish()
    
def console_test():
    global progress_x
    
    def start_progress(title):
        global progress_x
        sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
        sys.stdout.flush()
        progress_x = 0

    def progress(x):
        global progress_x
        x = int(x * 40 // 100)
        sys.stdout.write("#" * (x - progress_x))
        sys.stdout.flush()
        progress_x = x

    def end_progress():
        sys.stdout.write("#" * (40 - progress_x) + "]\n")
        sys.stdout.flush()
        
    start_progress('Test')
    
    for i in range(100):
        progress(i)
        sleep(.02)
        
    end_progress()

def console_test1():
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

        print(f'{title}: [{done_str}{togo_str}] {percent_done}% done', end='\r')

        if round(percent_done) == 100:
            print(' ' * 80, flush=True)


    r = 50
    for i in range(r):
        print_percent_done(i,r)
        sleep(.02)
        
def emex_find_maker():
    pattern = re.compile('kashiyama', re.I)
    
    def find_makers(tag):
        return tag.name == 'a' and tag.findChild(string=pattern)
    
    response = requests.get('https://emex.ru/products/K2342')
    soup = BeautifulSoup(response.text)
    result = soup.find_all(find_makers)
    print(result)
    
    result = result[0].findChild(string=pattern)
    print(type(result))
    print(result)
    # print([pattern.search(r) for item in result for r in item.findChild(string=pattern)])

def main():
    # exist_test()
    # emex_test()
    # xls_test()
    # writer_test()
    # console_test()
    # console_test1()
    emex_find_maker()
    

if __name__ == '__main__':
    main()
    