from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import re
import json

url = "https://exist.ru/Price/Default.aspx/GetQuery"

# cookies
# _go - office location
# _go=546 - Химки, Юбилейный проспект 7а


# payload = "{\n\tOriginalProductID: \"4880172F\",\n  ProductID: \"1920D70A\",\n  srcid: \"RawPartNumber\",\n  textValue: \"8f0bd5e2fab24823c0044a51e42465ca\"\n}"
# headers = {
#     "cookie": "_sc=qpk532zklipvq20qhok1qegh; _vs=69c30cc8-abf3-46fb-be5d-d66ed5501a60; _go=840; _lchd=1; _autd=1",
#     "authority": "exist.ru",
#     "accept": "*/*",
#     "content-type": "application/json; charset=UTF-8"
# }

# response = requests.request("POST", url, data=payload, headers=headers)

# print(response.text)

# Item structure
'''
{
    "expanded": false,
    "CatalogName": "Fortech",
    "CatalogId": 2583,
    "IsOriginal": false,
    "IsFav": false,
    "BlockText": "Предложения по заменителям",
    "BlockTypeId": 0,
    "ProdUrl": "/Parts.axd?pid=56E095DE\u0026flag=1064992",
    "ProductIdEnc": "56E095DE",
    "srcId": -4,
    "PartNumber": "FO......09",
    "Description": "Фильтр масляный",
    "InfoHTML": "\u003cspan class=\"img\"\u003e\u003c/span\u003e",
    "PriceCount": 1,
    "MoreOffers": 0,
    "restoredIcon": "",
    "AbsoluteRatingString": "0.5",
    "AbsoluteRating": "9",
    "sortField": "",
    "minPrice": 0,
    "maxPrice": 0,
    "AggregatedParts": [{
        "StatisticHTML": "\u003ca onclick=\u0027javascript: ShowTipLayer(this,event,this.href, 30,130); return false\u0027 target=\u0027_blank\u0027 href=\u0027/Price/hint/Graph.aspx?s=4880172F_01000b03e3002a7a031fa50601007a4c_779_-4\u0027\u003eПт 12:00\u003cspan\u003e\u003c/span\u003e\u003c/a\u003e",
        "price": 248,
        "priceString": "248 ₽",
        "avail": 0,
        "availString": "\u003ca title=\"Склад поставщика.Заказывайте в необходимом количестве\" class=\"gal\"\u003e\u003c/a\u003e",
        "days": 5,
        "pack": "",
        "InlineProductId": "4880172F_01000b03e3002a7a031fa50601007a4c_779_-4",
        "basketHTML": "\u003ca class=\"basket\" id=\"_4880172F_01000b03e3002a7a031fa50601007a4c_779_-4\" href=\"/Profile/Login?ReturnUrl=%2fPrice%2fdefault.aspx%3fpid%3d4880172F\" onclick=\"SsoUser.OpenLoginForm(event)\" target=\"_parent\" title=\"Купить\"\u003e\u003c/a\u003e",
        "highlightColor": null,
        "ProductIdEnc": "56E095DE"
    }],
    "DirectOffers": []
}
'''

# Security key
# To request additional items we need to send a request with a special security key rendered on the page
'''
'''

MAPPING = {
    'id': 'ProductIdEnc',
    'manufacturer': 'CatalogName',
    'part_number': 'PartNumber',
    'description': 'Description',
    'rating': 'AbsoluteRatingString',
    'children': 'AggregatedParts'
}

ITEM_MAPPING = {
    'amount': ('availString', lambda x: re.search(r'title="(.+?)"', x).group(1)),
    'price': 'price',
    'working_hours': ('StatisticHTML', lambda x: BeautifulSoup(x, features='html.parser').text),
    'delivery_duration': 'days'
}

def get_search_url(source, part_code):
    return source['search_url'].format(part_code = part_code)


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
    
    result = [['id', 'manufacturer', 'part_number', 'rating', 'description', 'amount', 'price', 'working_hours', 'delivery_duration']]
    
    for item in data:
        id = item[MAPPING['id']]
        manufacturer = item[MAPPING['manufacturer']]
        part_number = item[MAPPING['part_number']]
        rating = item[MAPPING['rating']]
        description = item[MAPPING['description']]
        children = item[MAPPING['children']]
        
        for entry in children:
            item_data = [id, manufacturer, part_number, rating, description]
    
            for key in ITEM_MAPPING:
                prop = ITEM_MAPPING[key]
                
                # value might be a tuple of key name and processor
                if type(prop) is tuple:
                    prop, handler = prop
                    item_data.append(handler(entry[prop]))
                else:
                    item_data.append(entry[prop])
            
            result.append(item_data)
        
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
    
    # url = get_search_url(SOURCE_EXIST, code)
        
    # return process_page(url, hint)
        