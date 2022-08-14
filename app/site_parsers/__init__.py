from .parser_exist.parser import handle as exist_handle
from .parser_emex.parser import handle as emex_handle

parsers = {
    'exist': exist_handle,
    'emex': emex_handle
}
    