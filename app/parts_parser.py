import site_parsers
import settings

def parse_part(code, hint):
    result = []
    
    # collect output from parsers
    for source in settings.SOURCES:
        handle = site_parsers.parsers[source['PARSER']]
        content = handle(code, hint)
        
        if content != None and len(content):
            result = result + content
        else:
            print('no content returned from the parser: ', source['PARSER'])
            
    return result
        