# -*- coding: utf-8 -*-
#
import excode

try:
    import StringIO as io
except ImportError:
    import io


def test_plain(get_file):
    with open(get_file.join("markdown/test_plain.md")) as inp:
        code_blocks = excode.extract(inp)
    assert len(code_blocks) == 1
    assert code_blocks[0] == "1 + 2 + 3\n"
    out = io.StringIO()
    excode.write(out, code_blocks, "python")
    assert (
        out.getvalue()
        == """def test0():
    1 + 2 + 3
    return
"""
    )
    return


def test_filter(get_file):
    with open(get_file.join("markdown/test_filter.md")) as inp:
        code_blocks = excode.extract(inp, filter_str="python")
    assert len(code_blocks) == 1
    assert code_blocks[0] == "1 + 2 + 3\n"
    return
