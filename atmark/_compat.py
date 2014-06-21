import sys


PY2 = sys.version_info[0] == 2


# Compat tools
if PY2:
    text_type = unicode
    string_decode = lambda b: text_type(b).decode('string_escape')
    string_types = (str, unicode)
else:
    text_type = str
    string_types = (str,)
    string_decode = lambda b: text_type(b.encode('utf-8').decode('unicode_escape'))


# pylama:ignore=E731
