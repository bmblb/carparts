import logging
import site_parsers
import settings

def parse_part(code, hint):
    # TODO: use asyncio to parallelize parsers here. each parser should write its own output
    for source in settings.SOURCES:
        logging.info('Running parser %s', source['PARSER'])
        
        handle = site_parsers.parsers[source['PARSER']]
        
        yield from handle(code, hint)
        