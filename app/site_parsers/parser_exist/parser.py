from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import re
import json
from settings import SOURCE_EXIST

def get_search_url(source, part_code):
    return source['SEARCH_URL'].format(part_code = part_code)


def get_page(url):
    response = requests.get(url)
    
    with open('tmp.html', 'w') as file:
        file.write(response.text)
    
    return response

def get_parts_data(response):
    soup = BeautifulSoup(response.text, features='html.parser')
    
    # find form with id which holds product data
    form = soup.find(attrs={'id':'form1'})
    
    # get the script with rendered JS object
    script = form.find('script')
    
    # grab contents of the js object
    contents = re.search(r'(\[{.+?(}\]));', script.contents[0]).group(1)
    
    data = json.loads(contents)
    
    result = []
    
    for item in data:
        result.append([1,2,3])
        
    return result

def process_page_content(response, hint):
    root = BeautifulSoup(response.text, features='html.parser')
    
    # if there is a picker for manufacturer we need to issue another request
    if root.find('ul', class_='catalogs'):
        catalog = root.find('ul', class_='catalogs')
        
        for anchor in catalog.find_all('a'): 
            # match manufacturer with the hint
            span = anchor.find('b')
            print(span)
            if span != None:
                contents = span.contents[0].lower()
                
                # if anchor content matches hint, get the href and load the page
                if contents == hint:
                    return process_page(urljoin(response.url, anchor['href']), hint)
    else:
        return get_parts_data(response)

def process_page(url, hint):
    r = get_page(url)
    
    if r.status_code == 200:
        return process_page_content(r, hint)
    else:
        print(r.status_code)

def handle(code, hint):
    print('exist')
    
    url = get_search_url(SOURCE_EXIST, code)
        
    return process_page(url, hint)
        