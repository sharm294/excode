# -*- coding: utf-8 -*-
#
import excode
import textwrap

try:
    import StringIO as io
except ImportError:
    import io


def test_plain(get_file):
    with open(get_file.join("markdown/test_plain.md")) as inp:
        extracted = excode.extract(inp)
    assert len(extracted["code_blocks"]) == 1
    target_value = textwrap.dedent(
        """\
        add = 1 + 2 + 3
        print(add)
        add = 4 + 5
        print(add)
    """
    )
    assert extracted["code_blocks"][0]["code"] == target_value
    out = io.StringIO()
    excode.write(out, extracted)
    target_value = textwrap.dedent(
        """\
        def test0():
            add = 1 + 2 + 3
            print(add)
            add = 4 + 5
            print(add)
            return
    """
    )
    assert out.getvalue() == target_value
    return


def test_filter(get_file):
    with open(get_file.join("markdown/test_filter.md")) as inp:
        extracted = excode.extract(inp, filter_str="python")
    assert len(extracted["code_blocks"]) == 1
    assert extracted["code_blocks"][0]["code"] == "1 + 2 + 3\n"
    return


def test_shell(get_file):
    with open(get_file.join("markdown/test_shell.md")) as inp:
        extracted = excode.extract(inp)
    assert len(extracted["code_blocks"]) == 1
    assert extracted["code_blocks"][0]["code"] == "export FOO=bar\n"
    out = io.StringIO()
    excode.write(out, extracted)
    target_value = textwrap.dedent(
        """\
        test0() {
            export FOO=bar
        }


        export NUM_TESTS=1
    """
    )
    assert out.getvalue() == target_value
    return
