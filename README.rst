The Atmark
##########

.. _description:

The Atmark -- Awk+sed for humans.

Do this: ::

    # Rename file in current directory (file-name -> file_name.jpg)
    $ ls | @ replace - _ "mv # @.jpg" | sh

Except this: ::

    # Rename file in current directory (file-name -> file_name.jpg)
    $ ls | awk '{print $1 $1}' | sed s/"-"/"_"/ | awk '{print "mv", $2, $1, ".jpg"}' | sh


More deep: ::

    $ ls | @  replace   -   _   "mv # @.jpg" | sh
              -------   |   |   ------------
                |       |   |       \_ format string (# - link on first state,
                |       |   |                         @ - link on current state (after replace))
                |       |   |
                |       |    \_ second replace param (to replace)
                |       |
                |        \_ first replace param (what replace)
                |
                 \_ function name (replace)

More examples: ::

    # Change files extension .html > .php

    # Atmark
    $ ls | grep .jpeg | @ split . head "mv # @.php"

    # Awk/Sed
    $ ls | awk '{printf "mv "$0; sub(/html/,"php"); print " "$0}' | sh


    # Print all but the first three columns

    # Atmark
    $ ls -la | @ split_ drop 3 join_

    # Awk/Sed
    $ ls -la | awk '{for(i=1;i<4;i++) $i="";print}'


    # Kill process by name
    # Atmark
    $ ps aux | @ grep sysmond$ index 2 "kill @" | sh 

    # Awk/Sed
    $ ps aux | grep [s]ysmond | awk '{print "kill "$2}' | sh


And more, more, more.

.. _badges:

.. image:: https://secure.travis-ci.org/klen/at.png?branch=develop
    :target: http://travis-ci.org/klen/at
    :alt: Build Status

.. image:: https://coveralls.io/repos//at/badge.png?branch=develop
    :target: https://coveralls.io/r/klen/at
    :alt: Coverals

.. image:: https://pypip.in/d/at/badge.png
    :target: https://pypi.python.org/pypi/at

.. image:: https://badge.fury.io/py/at.png
    :target: http://badge.fury.io/py/at

.. _documentation:

**Docs are available at https://at.readthedocs.org/. Pull requests
with documentation enhancements and/or fixes are awesome and most welcome.**

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 2.6

.. _installation:

Installation
=============

**The Atmark** should be installed using pip: ::

    pip install atmark

.. _usage:

Usage
=====

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/at/issues

.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/klen/at


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.com/
