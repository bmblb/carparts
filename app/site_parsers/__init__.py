import logging
from .parser_exist.parser import handle as exist_handle
from .parser_emex.parser import Emex

parsers = {
    'exist': exist_handle,
    'emex': Emex
}

def get_parser(config):
    name = config['PARSER']
    
    parser = parsers[name]
    
    if name in parsers:
        parser = parsers[name]()
        parser.init()
        
        if 'LOGIN' in config:
            logged = parser.login(config['LOGIN'], config['PASSWORD'])
        
            if logged:
                return parser
            else:
                logging.warn('Cannot login parser: %s', name)
        else:
            return parser
    else:
        logging.warning('Cannot find parser: %s', name)
        
    return None
        
