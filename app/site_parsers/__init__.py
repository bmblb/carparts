import logging
from .parser_exist.parser import handle as exist_handle
from .parser_emex.parser import Emex

parsers = {
    'exist': exist_handle,
    'emex': Emex
}

initialized = {}

def get_parser(config, delay):
    name = config['PARSER']
    
    parser = parsers[name]
    
    if name in initialized:
        return initialized[name]
    elif name in parsers:
        parser = parsers[name](delay=delay)
        
        initialized[name] = parser
        
        if 'LOGIN' in config:
            logged = parser.login(config.get('LOGIN', ''), config.get('PASSWORD', ''))
        
            if logged:
                return parser
            else:
                logging.warn('Cannot login parser: %s', name)
        else:
            return parser
    else:
        logging.warning('Cannot find parser: %s', name)
        
    return None
        
