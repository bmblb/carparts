import logging
from .parser_exist.parser import handle as exist_handle
from .parser_emex.parser import Emex

parsers = {
    'exist': exist_handle,
    'emex': Emex
}

initialized = {}

def get_parser(config, delay):
    name = config.get('name')
    
    parser = parsers[name]
    
    if name in initialized:
        return initialized[name]
    elif name in parsers:
        parser = parsers[name](delay=delay)
        
        initialized[name] = parser
        
        return parser if parser.login(config.get('login', ''), config.get('password', '')) else None
    else:
        logging.warning('Cannot find parser: %s', name)
        
    return None
        
