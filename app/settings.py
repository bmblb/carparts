import os, configparser

config = configparser.ConfigParser()

# Path to in/out dirs relative to the main.py
INPUT_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'input'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', 'output'))

config_path = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'app.ini'))

if os.path.exists(config_path):
    config.read(config_path)

if config.has_section('app'):
    INPUT_DIR = config['app'].get('input_path', INPUT_DIR)
    OUTPUT_DIR = config['app'].get('output_path', OUTPUT_DIR)

# Timeout between requests in milliseconds
REQUEST_TIMEOUT = 60000

SOURCES = {
    "emex": {
        'name': 'emex',
        'search_url': 'https://emex.ru/products/{part_code}'
    }
}

for section in [s for s in config.sections() if s.startswith('parser_')]:
    name = section.replace('parser_', '')
    
    if name in SOURCES:
        SOURCE = SOURCES.get(name)
        
        for key, value in config[section].items():
            SOURCE[key] = value
 
SOURCES = [v for v in SOURCES.values()]
