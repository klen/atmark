import re

from functools import wraps

from .utils import style, unicode_escape, text_type


AT_COMMANDS = dict()
AT_COMMANDS_DOCS = style("""
===================================================================================
LIST OF THE BUILT IN FUNCTIONS
""", fg='yellow')
CURRENT_RE = re.compile(r'(?=[^\\]?)@')
HISTORY_RE = re.compile(r'(?=[^\\]?)#(\d)*')


def _command(nump=0, *syns):
    """ Save function as At command. """

    def decorator(func):
        name = func.__name__[3:]
        AT_COMMANDS[name] = func, nump
        global AT_COMMANDS_DOCS
        AT_COMMANDS_DOCS += "\n\n" + (func.__doc__ or "%s") % "/".join(
            style(n, fg='yellow') for n in (name,) + syns)
        for syn in syns or []:
            AT_COMMANDS[syn] = func, nump

        @wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper

    return decorator


@_command(1)
def at_format(arg, pattern):
    """ %s PATTERN \t -- format and print a string.

    Symbol '@' in PATTERN represents the current value in process of composition of fuctions.
    Symbol '#' in PATTERN represents the history state.
        Where   # or #0 -- first state, #<n> (#1, #2) -- state with number n

    Synonyms: You can drop `format` function name. This lines are equalent:

        $ ls | @ upper format "@.BAK"
        $ ls | @ upper "@.BAK" """
    pattern, _ = unicode_escape(pattern)
    value = text_type(arg)
    value = CURRENT_RE.sub(value, pattern)

    def get_history(m):
        index = int(m.group(1) or 0)
        return text_type(arg.history[index])
    value = HISTORY_RE.sub(get_history, value)
    return value


@_command(0, 'cap')
def at_capitalize(arg):
    """ %s \t -- capitalize the string. """
    value = text_type(arg)
    return value[0].upper() + value[1:].lower()


@_command(1)
def at_drop(arg, length):
    """ %s N \t\t -- drop N elements from list/string. """
    return arg.value[int(length):]


@_command(1, '==')
def at_equal(arg, pattern):
    """ %s PATTERN \t -- return None if arg is not equal to PATTERN. """
    value = text_type(arg)
    if value == pattern:
        return value


@_command(0, 'if')
def at_filter(arg):
    """ %s \t\t -- filter results by value has length """
    if isinstance(arg.value, list):
        return arg.value or None
    return arg.value.strip() or None


@_command(0, 'h')
def at_head(arg):
    """ %s \t\t -- extract the first element/character of a list/string """
    return arg.value and arg.value[0] or None


@_command(1, 'ix', 'i')
def at_index(arg, index):
    """ %s N \t\t -- get the N-th element/character from list/string. """
    try:
        index = int(index)
    except ValueError:
        return None
    return arg.value[index]


@_command(1, 'j')
def at_join(arg, sep):
    """ %s SEPARATOR \t -- concatenate a list/string with intervening occurrences of SEPARATOR """
    sep, _ = unicode_escape(sep)
    return sep.join(arg.value)


@_command(0, 'j_')
def at_join_(arg):
    """ %s \t\t -- same as join but SEPARATOR set as ' ' """
    return " ".join(arg.value)


@_command()
def at_last(arg):
    """ %s \t\t\t -- get last element/character of incoming list/string. """
    return arg.value[-1]


@_command(0, 'len')
def at_length(arg):
    """ %s \t\t -- return length of list/string. """
    return text_type(len(arg.value))


@_command(0, 'l')
def at_lower(arg):
    """ %s \t\t -- make the string is lowercase """
    value = text_type(arg)
    return value.lower()


@_command(1)
def at_map(arg, func, *params):
    """ %s FUNCTION \t\t -- apply the following function to each element/character in list/string. """ # noqa
    return [func(el, *params) for el in arg.value]


@_command(1, '!=')
def at_notequal(arg, pattern):
    """ %s PATTERN \t -- return None if arg is equal to PATTERN. """
    value = text_type(arg)
    if value != pattern:
        return value


@_command(2, 'r', 'sub')
def at_replace(arg, p1, p2):
    """ %s FROM TO \t -- replace in a string/list FROM to TO. """
    value = text_type(arg)
    return value.replace(p1, p2)


@_command(0, 'rev')
def at_reverse(arg):
    """ %s \t\t -- reverse list/string. """
    return arg.value[::-1]


@_command(1, 'rs', 'rtrim')
def at_rstrip(arg, pattern):
    """ %s PATTERN -- return the string with trailing PATTERN removed. """
    value = text_type(arg)
    return value.rstrip(pattern)


@_command(1, 'g')
def at_grep(arg, regexp):
    """ %s REGEXP \t\t -- filter results by REGEXP """
    value = text_type(arg.value)
    if re.search(regexp, value):
        return arg.value


@_command()
def at_sort(arg):
    """ %s \t\t\t -- sort list/string. """
    return list(sorted(arg.value))


@_command(1, 'sp')
def at_split(arg, p):
    """ %s SEPARATOR \t -- return a list of the substrings of the string splited by SEPARATOR """
    value = text_type(arg)
    try:
        return value.split(p)
    except ValueError:
        return None


@_command(0, 'sp_')
def at_split_(arg):
    """ %s \t\t -- same as split by splited a string by whitespace characters """
    value = text_type(arg)
    return value.split()


@_command(1, 's', 'trim')
def at_strip(arg, pattern):
    """ %s PATTERN \t -- return the string with leading and trailing PATTERN removed. """
    value = text_type(arg)
    return value.strip(pattern)


@_command(0, 's_', 'trim_')
def at_strip_(arg):
    """ %s \t -- same as strip but trims a whitespaces. """
    value = text_type(arg)
    return value.strip()


@_command(0, 't')
def at_tail(arg):
    """ %s \t\t -- extract the elements after the head of a list """
    return arg.value[1:]


@_command(1)
def at_take(arg, length):
    """ %s N \t\t -- take N elements from list/string. """
    return arg.value[:int(length)]


@_command(0, 'u')
def at_upper(arg):
    """ %s \t\t -- make the string is uppercase. """
    value = text_type(arg)
    return value.upper()


# pylama:ignore=W0603
