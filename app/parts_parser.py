import settings
import requests

def get_search_url(source, part_code):
    return source['SEARCH_URL'].format(part_code = part_code)

def parse(code, hint):
    for source in settings.SOURCES:
        url = get_search_url(source, code)
        
        r = requests.get(url)
        
        print(r.status_code)
        