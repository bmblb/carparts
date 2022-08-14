from time import sleep, time
from bs4 import BeautifulSoup
from requests import request, Response
import re
import logging

'''
Emex has a proper API we could use to get JSON objects from the backend
Request:
https://emex.ru/api/search/search?detailNum=9091510001&locationId=31448&showAll=true&longitude=44.6926&latitude=39.8564
detailNum - articul
locationId - id of the drop point
showAll - self explanatory
longitude/latitude - geolocation of the client dd.dddd

Response:
{
    searchResult: Result
    errorMessage: String
}

Result:
{
    makes: {
        header: String,
        list: Manufacturer
    },
    originals: Detail[],
    replacements: Detail[]
}

Manufacturer:
{
    id: Number
    make: String (e.g. Toyota)
    num: String (articul)
    name: String (e.g. Масляный фильтр)
    url: String (e.g. url part "/9091510001/toyota/31448"),
    bestPrice: {
        value: Number
    }
}

Detail:
{
    detailKey: String
    productId: String
    detailNum: String (articul)
    make: String (e.g. Toyota, Daihatsu)
    name: String (e.g. масляный фильтр)
    offers: Offer[]
}

Offer:
{
    quantity: Number
    displayPrice: { value: Number }
    delivery: { value: Number, units: String }
    rating2: { value: Number }
}
'''

LAT = 37.430390
LNG = 55.888740
LOC_ID = 31448
SEARCH_URL = 'https://emex.ru/api/search/search?detailNum={art}&make={make}&locationId={locid}&showAll=true&longitude={lng}&latitude={lat}'

MAPPING = {
    'id': 'detailKey',
    'manufacturer': 'make',
    'part_number': 'formattedDetailNum',
    'description': 'name'
}

OFFER_MAPPING = {
    'rating': 'rating2.value',
    'amount': 'quantity',
    'price': 'displayPrice.value',
    'working_hours': '',
    'delivery_duration': ('delivery', lambda x: '{value} {units}'.format(**x))
}

ITEM_MAPPING = {
    'amount': ('availString', lambda x: re.search(r'title="(.+?)"', x).group(1)),
    'price': 'price',
    'working_hours': ('StatisticHTML', lambda x: BeautifulSoup(x, features='html.parser').text),
    'delivery_duration': 'days'
}

HEADERS = {
    'cookie': 'last-location=31448',
    'Access-Control-Allow-Origin': 'https://emex.ru',
    'Cache-Control': 'no-cache',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77'
}

def get_key(map, key, target):
    prop = map[key]
    accessor = lambda x: x
    
    if type(map[key]) is tuple:
        prop, accessor = map[key]
    
    # if target key name is empty return empty string
    if prop == '':
        target = ''
    # otherwise split key into chunks and dive into dictionary looking for value
    else:
        for part in prop.split('.'):
            if part in target:
                target = target[part]
            # if key is not in target use empty string for value
            else:
                target = ''
    
    return accessor(target)

def get_data_from_json(data, code):
    originals = data['searchResult']['originals']
    analogs = data['searchResult']['analogs']
    
    if len(originals) == 0:
        logging.warning('No originals for %s', code)
    
    if len(analogs) == 0:
        logging.warning('No analongs for %s', code)
    
    sources = [originals, analogs]
    
    for source in sources:
        for item in source:
            # code,id,manufacturer,part_number,rating,description,amount,price,working_hours,delivery_duration
            for offer in item['offers']:
                yield [
                    code,
                    get_key(MAPPING, 'id', item),
                    get_key(MAPPING, 'manufacturer', item),
                    get_key(MAPPING, 'part_number', item),
                    get_key(OFFER_MAPPING, 'rating', offer),
                    get_key(MAPPING, 'description', item),
                    get_key(OFFER_MAPPING, 'amount', offer),
                    get_key(OFFER_MAPPING, 'price', offer),
                    get_key(OFFER_MAPPING, 'working_hours', offer),
                    get_key(OFFER_MAPPING, 'delivery_duration', offer),
                ]

global LAST_CALL_TIME

LAST_CALL_TIME = 0

def handle(code, hint):
    global LAST_CALL_TIME
    
    logger = logging.getLogger(__name__)
    
    logger.info('Processing %s %s', code, hint)
    print(time(), LAST_CALL_TIME)
    # calculate time since last run
    passed_time = time() - LAST_CALL_TIME
    
    if passed_time < 10:
        delay = round(10 - passed_time)
        logger.info('Sleeping for %s', delay)
        # if not, sleep for some time
        sleep(delay)
    else:
        logger.info('Making request asap')
    
    # after we've waited store the current time as last call time
    LAST_CALL_TIME = time()
    
    response: Response = request('GET', SEARCH_URL.format(art=code, make=hint, lat=LAT, lng=LNG, locid=LOC_ID), headers=HEADERS)
    
    if response.status_code != 200:
        logger.warning('Request to URL did not end up well')
        logger.warning('URL: %s', response.url)
        logger.warning('Code: %s', response.status_code)
        
        yield ''
    else:
        data = response.json()
        
        if data['errorMessage'] != '':
            logger.error('Error searching for detail number: %s', code)
            logger.error(data['errorMessage'])
            
            yield ''
        else:
            yield from get_data_from_json(data, code)

