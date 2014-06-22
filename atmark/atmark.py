"""

Atmark (@) -- is a command line utility for parsing text input and generating output.

You can pipe data within a Atmark (@) statement using standard unix style pipes ("|").
Provide for Atmark function composition and let them work for you.

Example. Replace "_" with "-" in files in current dir and change the files extensions to jpg:

    $ ls | @ replace _ -  split . "mv # @.jpg"

It is mean:

    $ ls > replace($LINE, "_", "-") > split($RESULT, ".") > format($RESULT, "mv $LINE $RESULT.jpg")

You can use "@ --debug ARGS" for debug Armark commands. """
import os
import sys

from ._bashcomplete import do_complete, COMPLETION_SCRIPT
from .commands import AT_COMMANDS, at_format, AT_COMMANDS_DOCS
from .utils import echo, style, get_stream, ANSI, text_type


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
    for line in stream:
        arg = Arg(line).process(tokens)
        if arg.value is not None:
            yield arg


def _atat(args, stream):
    tokens = list(_tokenize(args))
    arg = Arg(list(stream)).process(tokens)
    if not isinstance(arg.value, list):
        return [arg.value]
    return arg.value


def _cli(func, args):
    if os.environ.get('_ATMARK_COMPLETE'):
        return do_complete()

    if args:
        if args[0] in ('-h', '--help'):
            echo(style(__doc__, bold=True, fg='green'))
            echo(AT_COMMANDS_DOCS)
            sys.exit()

        elif args[0] in ('-d', '--debug'):
            args.pop(0)

            def gen():
                while True:
                    for c in ANSI.colors[1:7]:
                        yield c
            gen = gen()

            stream = get_stream()
            for arg in func(args, stream):
                color = next(gen)
                echo("\n".join(
                    style("#%d" % num + " " + text_type(state), fg=color)
                    for num, state in enumerate(arg.history)))
            sys.exit()

        elif args[0] in ('-bs', '--bash-source'):
            return echo(COMPLETION_SCRIPT)

    stream = get_stream()
    for arg in func(args, stream):
        echo(arg)

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


at = lambda: _cli(_at, sys.argv[1:])
atat = lambda: _cli(_atat, sys.argv[1:])


if __name__ == '__main__':
    at()

# pylama:ignore=E731
