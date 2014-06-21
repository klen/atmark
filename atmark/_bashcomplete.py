import os
from .commands import AT_COMMANDS
from .utils import echo


COMPLETION_SCRIPT = """
_atmark_complete() {
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _ATMARK_COMPLETE=complete $1 ) )
    return 0
}

complete -F _atmark_complete -o default @ @@;
"""


def do_complete():
    cwords = os.environ['COMP_WORDS'].split()
    cword = int(os.environ['COMP_CWORD'])
    incomplete = previous = ""
    try:
        incomplete = cwords[cword]
    except IndexError:
        pass

    try:
        previous = cwords[cword - 1]
    except IndexError:
        pass

    if previous in AT_COMMANDS:
        _, nump = AT_COMMANDS.get(previous)
        if nump:
            return False

    for item in AT_COMMANDS.keys():
        if item.startswith(incomplete):
            echo(item)

    return True
