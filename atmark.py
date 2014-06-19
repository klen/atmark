""" At magic. """

# Package information
# ===================

__version__ = "0.1.0"
__project__ = "atmark"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"


import sys
from re import compile as re
from functools import wraps


AT_COMMANDS = {}


def at_command(nump=0, *syns):
    """ Save function as At command. """

    def decorator(func):
        AT_COMMANDS[func.__name__[3:]] = func, nump
        for syn in syns or []:
            AT_COMMANDS[syn] = func, nump

        @wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper

    return decorator


@at_command(1)
def at_format(arg, pattern):
    value = str(arg)
    return pattern.replace('@', value).replace('#', arg.sstart)


@at_command(2, 'r')
def at_replace(arg, p1, p2):
    value = str(arg)
    return value.replace(p1, p2)


@at_command(0, 'u')
def at_upper(arg):
    value = str(arg)
    return value.upper()


@at_command(0, 'l')
def at_lower(arg):
    value = str(arg)
    return value.lower()


@at_command(0, 'c')
def at_capitalize(arg):
    value = str(arg)
    return value[0].upper() + value[1:].lower()


@at_command(1, 's')
def at_strip(arg, pattern):
    value = str(arg)
    return value.strip(pattern)


@at_command(1, 'rs')
def at_rstrip(arg, pattern):
    value = str(arg)
    return value.rstrip(pattern)


@at_command(1, 'sp')
def at_split(arg, p):
    value = str(arg)
    return value.split(p)


@at_command(0, 'sp_')
def at_split_(arg):
    value = str(arg)
    return value.split()


@at_command(0, 'h')
def at_head(arg):
    return arg.value[0]


@at_command(0, 't')
def at_tail(arg):
    return arg.value[1:]


@at_command(1, 'j')
def at_join(arg, sep):
    return sep.join(arg.value)


@at_command(1, 'j_')
def at_join_(arg):
    return " ".join(arg.value)


@at_command(0, 'len')
def at_length(arg):
    return str(len(arg.value))


@at_command(0, 'if')
def at_filter(arg):
    if isinstance(arg.value, list):
        return arg.value or None
    return arg.value.strip() or None


@at_command(1, 'g')
def at_grep(arg, pattern):
    values = arg.value
    pattern = re(pattern)
    if not isinstance(values, list):
        values = [values]
    for v in values:
        if pattern.search(v):
            return arg.value
    return None


@at_command()
def at_last(arg):
    return arg.value[-1]


@at_command(1, 'ix', 'i')
def at_index(arg, index):
    return arg.value[index]


@at_command(1)
def at_take(arg, length):
    return arg.value[:int(length)]


@at_command(1)
def at_drop(arg, length):
    return arg.value[int(length):]


@at_command()
def at_sort(arg):
    return sorted(arg.value)


@at_command()
def at_reverse(arg):
    return reversed(arg.value)


class Arg(object):

    """ Store changes history. """

    def __init__(self, value=""):
        self.start = value
        self.value = value
        self.history = [value]
        self.sstart = str(self)

    def __repr__(self):
        return " > ".join(str(h) for h in self.history)

    def __str__(self):
        if isinstance(self.value, list):
            return "".join(self.value)
        return str(self.value)

    def process(self, tokens):
        for func, params in tokens:
            self.update(func(self, *params))
            if self.value is None:
                break
        return self

    def update(self, value):
        self.value = value
        self.history.append(value)


def _at(args, stream=None):
    tokens = list(_tokenize(args))
    stream = _get_stream(stream)
    for arg in stream:
        arg = Arg(arg).process(tokens)
        if arg.value is None:
            continue
        yield arg


def _atat(args, stream=None):
    tokens = list(_tokenize(args))
    stream = _get_stream(stream)
    arg = Arg(stream).process(tokens)
    if not isinstance(arg.value, list):
        return [arg.value]
    return arg.value


def _tokenize(args):
    try:
        while args:
            arg = args.pop(0).strip()
            if arg in AT_COMMANDS:
                (func, nump), params = AT_COMMANDS[arg], []
                while nump:
                    params.append(args.pop(0))
                    nump -= 1
                yield func, params
                continue
            yield at_format, [arg]
    except IndexError:
        yield at_format, ['@']


def _get_stream(stream):
    if not stream and not sys.stdin.isatty():
        return list(l.strip() for l in sys.stdin.readlines() if l.strip())
    return stream or []


def _cli(func, args):
    for arg in func(args):
        if arg.value is not None:
            print arg


at = lambda: _cli(_at, sys.argv[1:])
atat = lambda: _cli(_atat, sys.argv[1:])


if __name__ == '__main__':
    at()

# pylama:ignore=E731
