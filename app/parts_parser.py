import logging
import site_parsers
import settings

def init_parsers():
    parsers = []
    
    for source in settings.SOURCES:
        parser = site_parsers.get_parser(source)
        
        if parser != None:
            parsers.append(parser)
            
    return parsers

def parse_part(code, hint):
    parsers = init_parsers()
    
    if len(parsers) == 0:
        logging.info('Could not initialize any parsers')
        yield ''
    else:
        # TODO: use asyncio to parallelize parsers here. each parser should write its own output
        for parser in parsers:
            logging.info('Running parser %s', parser.name)
            
            yield from parser.handle(code, hint)
        