import codecs
import sys
from re import compile as re


ANSI = lambda: None
ANSI.colors = 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'reset'
ANSI.reset = '\033[0m'
ANSI.re = re(r'\033\[((?:\d|;)*)([a-zA-Z])')
PY2 = sys.version_info[0] == 2


def isatty(stream):
    try:
        return stream.isatty()
    except (AttributeError, TypeError):
        return False


if PY2:
    from cStringIO import StringIO

    text_type = unicode
    string_types = (str, unicode)
    is_bytes = lambda x: isinstance(x, (buffer, bytearray))

else:
    from io import StringIO

    text_type = str
    string_types = (str,)
    is_bytes = lambda x: isinstance(x, (bytes, bytearray))


def get_stream(stream=sys.stdin):

    if isatty(stream):
        stream = StringIO()

    encoding = getattr(stream, 'encoding', None) or sys.getdefaultencoding()
    if codecs.lookup(encoding).name == 'ascii':
        encoding = 'utf-8'
    codecs.getwriter(encoding)(sys.stdout)

    def gen():
        for line in stream.readlines():
            if not isinstance(line, text_type):
                line = line.decode(encoding)
            yield line.strip('\n\r')

    return gen()


def style(text, fg=None, bg=None, bold=None, dim=None, underline=None,
          blink=None, reverse=None, reset=True):
    bits = []
    if fg:
        try:
            bits.append('\033[%dm' % (ANSI.colors.index(fg) + 30))
        except ValueError:
            raise TypeError('Unknown color %r' % fg)
    if bg:
        try:
            bits.append('\033[%dm' % (ANSI.colors.index(bg) + 40))
        except ValueError:
            raise TypeError('Unknown color %r' % bg)
    if bold is not None:
        bits.append('\033[%dm' % (1 if bold else 22))
    if dim is not None:
        bits.append('\033[%dm' % (2 if dim else 22))
    if underline is not None:
        bits.append('\033[%dm' % (4 if underline else 24))
    if blink is not None:
        bits.append('\033[%dm' % (5 if blink else 25))
    if reverse is not None:
        bits.append('\033[%dm' % (7 if reverse else 27))
    bits.append(text)
    if reset:
        bits.append(ANSI.reset)
    return ''.join(bits)


def echo(message, nl=True):
    stream = sys.stdout

    if not isinstance(message, string_types):
        message = text_type(message)

    if not isatty(stream):
        message = ANSI.re.sub('', message)

    if message:
        stream.write(message)

    if nl:
        stream.write('\n')

    stream.flush()

unicode_escape = lambda s: codecs.getdecoder('unicode_escape')(s)[0]

# pylama:ignore=E731
