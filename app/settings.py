import settings_local, os

# Path to in/out dirs relative to the main.py
INPUT_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'input'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'output'))

# Timeout between requests in milliseconds
REQUEST_TIMEOUT = 60000

# exist
SOURCE_EXIST = {
    'SEARCH_URL': 'https://exist.ru/Price/?pcode={part_code}',
    'PARSER': 'exist'
}

SOURCE_EMEX = {
    'SEARCH_URL': 'https://emex.ru/products/{part_code}',
    'PARSER': 'emex'
}

if 'LOGIN' in dir(settings_local):
    SOURCE_EMEX['LOGIN'] = settings_local.EMEX_LOGIN
    SOURCE_EMEX['PASSWORD'] = settings_local.EMEX_PASSWORD

SOURCES = [SOURCE_EMEX]
