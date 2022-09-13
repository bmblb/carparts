import json
from time import sleep, time
from bs4 import BeautifulSoup
from requests import Response, Session, exceptions
import re
import logging
from time import time

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
# Москва, ПВЗ на Ленинградской 16Б в Химках
# Судя по всему работает только для анонимного пользователя, пункт выдачи привязан к аккаунту
LOC_ID = 30073
SEARCH_URL = 'https://emex.ru/api/search/search?detailNum={art}&make={make}&locationId={locid}&showAll=true&longitude={lng}&latitude={lat}'

# Производитель для каждой детали может отличаться. Например для одной Kashiyama, а для другой KASHIYAMA. Поэтому нужно понять как именно
# производитель зарегистрирован у емекса
MAKER_URL = 'https://emex.ru/products/{art}'

MAPPING = {
    'id': 'detailKey',
    'manufacturer': 'make',
    'part_number': 'formattedDetailNum',
    'description': 'name'
}

OFFER_MAPPING = {
    'supplier': 'rating2.code',
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
            target = target.get(part, '')
    
    return accessor(target)

class Emex():
    name = 'Emex'
    
    def __init__(self, delay=60):
        self.delay = delay
        
        session = Session()
        
        session.headers.update({
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            # no clue what it does, but just in case
            'Cache-Control': 'no-cache',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Origin': 'https://emex.ru',
            'Referer': 'https://emex.ru',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77'
        })
        
        session.cookies.set('Cookie', 'last-location={}'.format(LOC_ID))
        
        self.session = session
        self.authorized = False
        self.logger = logging.getLogger(__name__)
        self.LAST_REQUEST_TIME = 0
        
    def ensure_request_timeout(self):
        # calculate time since last run
        passed_time = time() - self.LAST_REQUEST_TIME
        
        if passed_time < self.delay:
            delay = round(self.delay - passed_time)
            self.logger.info('Sleeping for %s', delay)
            # print('EMEX: Sleep for {} sec'.format(delay))
            # if not, sleep for some time
            sleep(delay)
        
        # after we've waited store the current time as last call time
        self.LAST_REQUEST_TIME = time()
        
    def login(self, login, password):
        if not login or not password:
            self.logger.warning('Login or password is empty, skip login')
            return True
            
        self.ensure_request_timeout()
        
        res : Response = self.session.post('https://emex.ru/api/account/login', json={ 'login': login, 'password': password, 't': round(time() * 1000) })
        
        if res.status_code == 200:
            self.authorized = True
            self.logger.info(f'Logged in as {login}')
        else:
            self.logger.warning('Cannot login to emex')
            self.logger.warning(f'Code: {res.status_code}')
            
            try:
                self.logger.warning(res.json())
            except exceptions.JSONDecodeError:
                pass
            
        return self.authorized
    
    def get_manufacturer(self, code, hint) -> str:
        pattern = re.compile(hint, re.I)
        
        def find_maker(tag):
            child = tag.select_one('div > div') if tag.name == 'a' else None
            return child and pattern.search(child.text)
        
        self.ensure_request_timeout()
        
        response: Response = self.session.get(MAKER_URL.format(art=code))
        
        # If there was a redirect pick last part of the URL
        if len(response.history) > 0:
            result = response.url.split('/')[-1]
            self.logger.info(f'Only one manufaturer found for the detail {code}: {result}')
            return result
        
        soup = BeautifulSoup(response.text, features='html.parser')
        
        links = soup.find_all(find_maker)
        
        if len(links) > 1:
            self.logger.warning(f'More than one manufacturer with the same name found for detail {code}')
        elif len(links) == 0:
            self.logger.error(f'Cannot find maker for the detail {code}')
            return hint
        
        try:
            result = links[0].select_one('div > div').text
            self.logger.info(f'Detail: {code}, Manufaturer: {result} (suggested {result})')
            return result
        except BaseException as e:
            self.logger.info(f'There was a problem extracting manufacturer, using suggested value: {hint}')
            # fallback to hint if we couldn't find the real maker
            return hint
            
    def handle(self, code, hint):
        logger = self.logger
        
        logger.info('Processing %s %s', code, hint)
        # print('EMEX: Processing detail {} {}'.format(code, hint))
        
        hint = self.get_manufacturer(code, hint)
        
        self.ensure_request_timeout()
        
        logger.info('Requesting detail info')
        
        response: Response = self.session.get(SEARCH_URL.format(art=code, make=hint, lat=LAT, lng=LNG, locid=LOC_ID))
        
        if response.status_code != 200:
            logger.warning('Request to URL did not end up well')
            logger.warning('URL: %s', response.url)
            logger.warning('Code: %s', response.status_code)
            
            yield ''
        else:
            data = response.json()
            
            errorMessage = data.get('errorMessage')
            
            if errorMessage:
                logger.error('Error searching for detail number: %s', code)
                logger.error(errorMessage)
                
                yield ''
            else:
                yield from self.get_data_from_json(data, code)

    def get_data_from_json(self, data, code):
        logger = self.logger
        
        result = data.get('searchResult')
        
        location = result.get('location', '')
        
        if location:
            if 'locationId' in location:
                logger.info('Location id: %s, address: %s', location.get('locationId'), location.get('address', ''))
            else:
                logger.info('Location: %s', json.dumps(location))
        
        sources = []
        
        for key in ['originals', 'replacements', 'analogs']:
            source = result.get(key, None)
        
            if source:
                logger.info('%s: %s', key, len(source))
                sources.append(source)
                
        if len(sources) == 0:
            logger.warning(f'No items found for {code}! Check manufacturer name')
        
        for source in sources:
            for item in source:
                # code,id,manufacturer,part_number,rating,description,amount,price,working_hours,delivery_duration
                for offer in item.get('offers'):
                    yield [
                        code,
                        get_key(MAPPING, 'id', item),
                        get_key(MAPPING, 'manufacturer', item),
                        get_key(MAPPING, 'part_number', item),
                        get_key(OFFER_MAPPING, 'supplier', offer),
                        get_key(OFFER_MAPPING, 'rating', offer),
                        get_key(MAPPING, 'description', item),
                        # if quantity is 1000 and `isCustom` is true, emex shows `Под заказ`
                        'Под заказ' if offer.get('isCustom', '') and offer.get('quantity') == 1000 else offer.get('quantity'),
                        # get_key(OFFER_MAPPING, 'amount', offer),
                        get_key(OFFER_MAPPING, 'price', offer),
                        get_key(OFFER_MAPPING, 'working_hours', offer),
                        get_key(OFFER_MAPPING, 'delivery_duration', offer),
                    ]

