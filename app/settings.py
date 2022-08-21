import settings_local

# Path to in/out dirs relative to the main.py
INPUT_DIR = '../input'
OUTPUT_DIR = '../output'

# Timeout between requests in milliseconds
REQUEST_TIMEOUT = 60000

# exist
SOURCE_EXIST = {
    'SEARCH_URL': 'https://exist.ru/Price/?pcode={part_code}',
    'PARSER': 'exist'
}

SOURCE_EMEX = {
    'SEARCH_URL': 'https://emex.ru/products/{part_code}',
    'PARSER': 'emex',
    'LOGIN': settings_local.EMEX_LOGIN,
    'PASSWORD': settings_local.EMEX_PASSWORD
}

SOURCES = [SOURCE_EMEX]
