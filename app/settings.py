import settings_local, os, json

config = {}

# Hacky way of reading app.config.json in bundled app. We check if app.config.json exists on the same level as the running file.
# In bundled app when we run `app.exe` it will be next to exe. In dev mode it will not be.s
config_path = os.path.join(os.path.abspath(__file__), '..', 'app.config.json')
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as config:
        config = json.loads(config.read())
    

# Path to in/out dirs relative to the main.py
INPUT_DIR = config.get('input_path') or os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'input'))
OUTPUT_DIR = config.get('output_path') or os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'output'))

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
