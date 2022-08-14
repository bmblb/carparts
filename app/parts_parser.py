import site_parsers
import settings

def parse_part(code, hint):
    # collect output from parsers
    for source in settings.SOURCES:
        handle = site_parsers.parsers[source['PARSER']]
        
        yield from handle(code, hint)
        