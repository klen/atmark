#!/usr/bin/env python
# coding: utf-8

""" Tests for `atmark` module. """

import pytest # noqa


def test_at():
    # $@
    result = _at("test.py some-file")
    assert ["test.py", "some-file"] == result

    # $@ @.bak
    result = _at("test.py some-file", "@.bak")
    assert ["test.py.bak", "some-file.bak"] == result

    # $@ upper
    result = _at("test.py some-file", "upper")
    assert ["TEST.PY", "SOME-FILE"] == result

    # $@ split . head replace - _ "mv # @.jpg"
    result = _at("test.py some-file", 'split', '.', 'head', 'replace', '-', '_', 'mv # @.jpg')
    assert ["mv test.py test.jpg", "mv some-file some_file.jpg"] == result


def test_unicode():
    result = _at(u"ехали медведи", "upper")
    assert [u'ЕХАЛИ', u'МЕДВЕДИ'] == result


def test_history():
    result = _at("ab bc", "upper", "cap", "# #1 #2")
    assert result == ['ab AB Ab', 'bc BC Bc']

    result = _at("q we rty", "cap", "len", "#1 @")
    assert result == ['Q 1', 'We 2', 'Rty 3']


def test_atat():
    result = _atat("test.py some-file")
    assert ['test.py', 'some-file'] == result

    result = _atat("test.py some-file", "sort", "head")
    assert ['some-file'] == result


def test_cli():
    from atmark import _cli, _at as _
    with pytest.raises(SystemExit):
        _cli(_, [])


def test_errors():
    result = _at("test.py some-file", "replace", "-")
    assert ["test.py", "some-file"] == result

    result = _at("test.py some-file", "upper", "replace", "-")
    assert ["TEST.PY", "SOME-FILE"] == result

    result = _atat("test.py some-file", "sort", "take")
    assert ['some-filetest.py'] == result

    result = _at("test.py some-file", "index", "lol")
    assert [] == result


def test_format():
    result = _at("test.py some-file", "format", "@_")
    assert ["test.py_", "some-file_"] == result

    result = _at("test.py some-file", "@_")
    assert ["test.py_", "some-file_"] == result

    result = _atat("test.py some-file", "@_")
    assert ["test.pysome-file_"] == result


def test_replace():
    result = _at("test.py some-file", "replace", "-", "_")
    assert ["test.py", "some_file"] == result

    result = _at("test.py some-file", "r", "-", "_")
    assert ["test.py", "some_file"] == result

    result = _atat("test.py some-file", "replace", "-", "_")
    assert ["test.pysome_file"] == result


def test_upper():
    result = _at("test.py some-file", "upper")
    assert ["TEST.PY", "SOME-FILE"] == result

    result = _at("test.py some-file", "u")
    assert ["TEST.PY", "SOME-FILE"] == result

    result = _atat("test.py some-file", "u")
    assert ["TEST.PYSOME-FILE"] == result


def test_lower():
    result = _at("tesT.py Some-file", "lower")
    assert ["test.py", "some-file"] == result

    result = _at("tesT.py Some-file", "l")
    assert ["test.py", "some-file"] == result

    result = _atat("tesT.py Some-file", "l")
    assert ["test.pysome-file"] == result


def test_capitalize():
    result = _at("tesT.py Some-file", "capitalize")
    assert ["Test.py", "Some-file"] == result

    result = _at("tesT.py Some-file", "cap")
    assert ["Test.py", "Some-file"] == result

    result = _atat("tesT.py Some-file", "cap")
    assert ["Test.pysome-file"] == result


def test_strip():
    result = _at("/test.py/ /some-file/", "strip", "/")
    assert ["test.py", "some-file"] == result

    result = _at("/test.py/ /some-file/", "s", "/")
    assert ["test.py", "some-file"] == result

    result = _atat("/test.py/ /some-file/", "s", "/")
    assert ["test.py//some-file"] == result


def test_rstrip():
    result = _at("/test.py/ /some-file/", "rstrip", "/")
    assert ["/test.py", "/some-file"] == result

    result = _at("/test.py/ /some-file/", "rs", "/")
    assert ["/test.py", "/some-file"] == result

    result = _atat("/test.py/ /some-file/", "rs", "/")
    assert ["/test.py//some-file"] == result


def test_split():
    result = _at("/test.py /some-file", "split", ".")
    assert ["/testpy", "/some-file"] == result

    result = _at("/test.py /some-file", "sp", ".")
    assert ["/testpy", "/some-file"] == result

    result = _atat("/test.py /some-file", "sp", ".")
    assert ["/test", "py/some-file"] == result


def test_head():
    result = _at("/test.py /some-file", "split", ".", "head")
    assert ["/test", "/some-file"] == result

    result = _at("/test.py /some-file", "split", ".", "tail", "head")
    assert ["py"] == result

    result = _at("/test.py /some-file", "split", ".", "h")
    assert ["/test", "/some-file"] == result

    result = _atat("/test.py /some-file", "h")
    assert ["/test.py"] == result


def test_tail():
    result = _at("/test.py /some-file", "split", ".", "tail")
    assert ["py", ""] == result

    result = _at("/test.py /some-file", "split", ".", "t")
    assert ["py", ""] == result

    result = _atat("/test.py /some-file", "t")
    assert ["/some-file"] == result


def test_take():
    result = _at("100 200 300 400", "take", 2)
    assert ["10", "20", "30", "40"] == result

    result = _atat("100 200 300 400", "take", 2)
    assert ["100", "200"] == result


def test_drop():
    result = _at("100 200 300 400", "drop", 2)
    assert ["0", "0", "0", "0"] == result

    result = _atat("100 200 300 400", "drop", 2)
    assert ["300", "400"] == result


def test_index():
    result = _at("100 200 300 400", "index", '0')
    assert ["1", "2", "3", "4"] == result

    result = _at("100 200 300 400", "ix", '0')
    assert ["1", "2", "3", "4"] == result

    result = _atat("100 200 300 400", "index", '2')
    assert ["300"] == result


def test_join():
    result = _at("/test.py /some-file", "split", ".", "join", "\\t")
    assert ["/test\tpy", "/some-file"] == result

    result = _at("/test.py /some-file", "split", ".", "j", ":")
    assert ["/test:py", "/some-file"] == result

    result = _atat("/test.py /some-file", "j", ">")
    assert ["/test.py>/some-file"] == result


def test_length():
    result = _at("/test.py /some-file", "split", ".", "length")
    assert ['2', '1'] == result

    result = _at("/test.py /some-file", "split", ".", "len")
    assert ['2', '1'] == result

    result = _atat("/test.py /some-file", "len")
    assert ['2'] == result


def test_filter():
    result = _at("/test.py /some-file", "split", ".", "tail", "filter")
    assert ['py'] == result

    result = _at("/test.py /some-file", "split", ".", "tail", "if")
    assert ['py'] == result


def test_grep():
    result = _at("/test.py /some-file", "grep", r"\.py$")
    assert ['/test.py'] == result

    result = _at("/test.py /some-file", "g", r"\.py$")
    assert ['/test.py'] == result


def _at(stream, *chain):
    from atmark import _at as _, text_type
    stream = stream.split()
    return list(map(text_type, _(list(chain), stream=stream)))


def _atat(stream, *chain):
    from atmark import _atat as _
    stream = stream.split()
    return _(list(chain), stream=stream)
