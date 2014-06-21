"""

Atmark (@) -- is a command line utility for parsing text input and generating output.

You can pipe data within a Atmark (@) statement using standard unix style pipes ("|").
Provide for Atmark function composition and let them work for you.

Example. Replace "_" with "-" in files in current dir and change the files extensions to jpg:

    $ ls | @ replace _ -  split . "mv # @.jpg"

It is mean:

    $ ls > replace($LINE, "_", "-") > split($RESULT, ".") > format($RESULT, "mv $LINE $RESULT.jpg")

You can use "@ --debug ARGS" for debug Armark commands.

===================================================================================
LIST OF THE BUILT IN FUNCTIONS

"""

from __future__ import print_function

# Package information
# ===================

__version__ = "0.5.1"
__project__ = "atmark"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"

import sys
import codecs
from functools import wraps
from re import compile as re


AT_COMMANDS = {}
PY2 = sys.version_info[0] == 2

CURRENT_RE = re(r'(?=[^\\]?)@')
HISTORY_RE = re(r'(?=[^\\]?)#(\d)*')


def _command(nump=0, *syns):
    """ Save function as At command. """

    def decorator(func):
        name = func.__name__[3:]
        AT_COMMANDS[name] = func, nump
        global __doc__                  # noqa
        __doc__ += "\n\n" + (func.__doc__ or "%s") % "/".join((name,) + syns)   # noqa
        for syn in syns or []:
            AT_COMMANDS[syn] = func, nump

        @wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper

    return decorator


@_command(1)
def at_format(arg, pattern):
    """ %s PATTERN -- format and print a string.

    Symbol '@' in PATTERN represents the current value in process of composition of fuctions.
    Symbol '#' in PATTERN represents the history state.
        Where   # or #0 -- first state, #<n> (#1, #2) -- state with number n

    Synonyms: You can drop `format` function name. This lines are equalent:

        $ ls | @ upper format "@.BAK"
        $ ls | @ upper "@.BAK" """
    pattern = string_decode(pattern)
    value = text_type(arg)
    value = CURRENT_RE.sub(value, pattern)

    def get_history(m):
        index = int(m.group(1) or 0)
        return text_type(arg.history[index])
    value = HISTORY_RE.sub(get_history, value)
    return value


@_command(0, 'cap')
def at_capitalize(arg):
    """ %s -- capitalize the string. """
    value = text_type(arg)
    return value[0].upper() + value[1:].lower()


@_command(1)
def at_drop(arg, length):
    """ %s N -- drop N elements from list/string. """
    return arg.value[int(length):]


@_command(0, 'if')
def at_filter(arg):
    """ %s -- filter results by value has length """
    if isinstance(arg.value, list):
        return arg.value or None
    return arg.value.strip() or None


@_command(1, 'g')
def at_grep(arg, regexp):
    """ %s REGEXP -- filter results by REGEXP """
    values = arg.value
    regexp = re(regexp)
    if not isinstance(values, list):
        values = [values]
    for v in values:
        if regexp.search(v):
            return arg.value
    return None


@_command(0, 'h')
def at_head(arg):
    """ %s -- extract the first element/character of a list/string """
    return arg.value and arg.value[0] or None


@_command(1, 'ix', 'i')
def at_index(arg, index):
    """ %s N -- get the N-th element/character from list/string. """
    try:
        index = int(index)
    except ValueError:
        return None
    return arg.value[index]


@_command(1, 'j')
def at_join(arg, sep):
    """ %s SEPARATOR -- concatenate a list/string with intervening occurrences of SEPARATOR """
    sep = string_decode(sep)
    return sep.join(arg.value)


@_command(0, 'j_')
def at_join_(arg):
    """ %s -- same as join but SEPARATOR set as ' ' """
    return " ".join(arg.value)


@_command()
def at_last(arg):
    """ %s -- get last element/character of incoming list/string. """
    return arg.value[-1]


@_command(0, 'len')
def at_length(arg):
    """ %s -- return length of list/string. """
    return text_type(len(arg.value))


@_command(0, 'l')
def at_lower(arg):
    """ %s -- make the string is lowercase """
    value = text_type(arg)
    return value.lower()


@_command(1)
def at_map(arg, func, *params):
    """ %s FUNCTION -- apply the following function to each element/character in list/string. """
    return [func(el, *params) for el in arg.value]


@_command(2, 'r', 'sub')
def at_replace(arg, p1, p2):
    """ %s FROM TO -- replace in a string/list FROM to TO. """
    value = text_type(arg)
    return value.replace(p1, p2)


@_command()
def at_reverse(arg):
    """ %s -- reverse list/string. """
    return arg.value[::-1]


@_command(1, 'rs', 'rtrim')
def at_rstrip(arg, pattern):
    """ %s PATTERN -- return the string with trailing PATTERN removed. """
    value = text_type(arg)
    return value.rstrip(pattern)


@_command()
def at_sort(arg):
    """ %s -- sort list/string. """
    return list(sorted(arg.value))


@_command(1, 'sp')
def at_split(arg, p):
    """ %s SEPARATOR -- return a list of the substrings of the string splited by SEPARATOR """
    value = text_type(arg)
    return value.split(p)


@_command(0, 'sp_')
def at_split_(arg):
    """ %s -- same as split by splited a string by whitespace characters """
    value = text_type(arg)
    return value.split()


@_command(1, 's', 'trim')
def at_strip(arg, pattern):
    """ %s PATTERN -- return the string with leading and trailing PATTERN removed. """
    value = text_type(arg)
    return value.strip(pattern)


@_command(0, 's_', 'trim_')
def at_strip_(arg):
    """ %s -- same as strip but trims a whitespaces. """
    value = text_type(arg)
    return value.strip()


@_command(0, 't')
def at_tail(arg):
    """ %s -- extract the elements after the head of a list """
    return arg.value[1:]


@_command(1)
def at_take(arg, length):
    """ %s N -- take N elements from list/string. """
    return arg.value[:int(length)]


@_command(0, 'u')
def at_upper(arg):
    """ %s -- make the string is uppercase """
    value = text_type(arg)
    return value.upper()


class Arg(object):

    """ Store changes history. """

    def __init__(self, value=""):
        self.start = value
        self.value = value
        self.history = [value]

    def __repr__(self):
        return " > ".join(text_type(h) for h in self.history)

    def __str__(self):
        if isinstance(self.value, list):
            return "".join(self.value)
        return text_type(self.value)

    __unicode__ = __str__

    def process(self, tokens):
        for func, params in tokens:
            self.update(func(self, *params))
            if self.value is None:
                break
        return self

    def update(self, value):
        self.value = value
        self.history.append(value)


def _at(args, stream):
    tokens = list(_tokenize(args))
    for arg in stream:
        arg = Arg(arg).process(tokens)
        if arg.value is None:
            continue
        yield arg


def _atat(args, stream):
    tokens = list(_tokenize(args))
    arg = Arg(stream).process(tokens)
    if not isinstance(arg.value, list):
        return [arg.value]
    return arg.value


def _cli(func, args):
    stream = _get_stream()
    if args and args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit()
    mod = text_type
    if args and args[0] in ('-d', '--debug'):
        args.pop(0)
        mod = repr
    for arg in func(args, stream):
        print(mod(arg))
    sys.exit()


def _tokenize(args):

    def take_params(args, nump):
        """ Function description. """
        while nump:
            nump -= 1
            yield args.pop(0)

    try:
        while args:
            arg = args.pop(0).strip()
            if arg in AT_COMMANDS:
                func, nump = AT_COMMANDS[arg]
                params = list(take_params(args, nump)) if nump else []
                if arg == 'map':
                    f, nump = AT_COMMANDS[params[0]]
                    params = [f] + list(take_params(args, nump))
                yield func, params
                continue
            yield at_format, [arg]
    except IndexError:
        yield at_format, ['@']


def _get_stream():
    encoding = sys.getdefaultencoding()
    stream = []
    if sys.stdin.isatty():
        return stream

    encoding = sys.stdin.encoding or encoding
    if codecs.lookup(encoding).name == 'ascii':
        encoding = 'utf-8'
    codecs.getwriter(encoding)(sys.stdout)
    for line in sys.stdin.readlines():
        line = line.decode(encoding).strip()
        stream.append(line)
    return stream


__doc__ += "\n\n Current version: " + __version__

at = lambda: _cli(_at, sys.argv[1:])
atat = lambda: _cli(_atat, sys.argv[1:])


# Compat tools
if PY2:
    text_type = unicode
    string_decode = lambda b: text_type(b).decode('string_escape')
else:
    text_type = str
    string_decode = lambda b: text_type(b.encode('utf-8').decode('unicode_escape'))


if __name__ == '__main__':
    at()

# pylama:ignore=E731
