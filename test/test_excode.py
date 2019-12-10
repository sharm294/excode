# -*- coding: utf-8 -*-
#
import excode
import textwrap

try:
    import StringIO as io
except ImportError:
    import io


def get_out_file(root_path, filename):
    return


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
        def test_0():
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


def test_shell(get_file, get_out_dir):
    with open(get_file.join("markdown/test_shell.md")) as inp:
        extracted = excode.extract(inp)
    assert len(extracted["code_blocks"]) == 1
    assert extracted["code_blocks"][0]["code"] == "export FOO=bar\n"

    out = open(get_out_dir.join("/test_shell.sh"), "w")
    excode.write(out, extracted)

    target_value = textwrap.dedent(
        """\
        test_0() {
            export FOO=bar
        }

        if [[ $1 == 0 ]]; then
            test_0
        fi
    """
    )
    filepath = get_out_dir.join("/test_shell.sh")
    out = open(filepath, "r")
    assert "".join(out.readlines()) == target_value

    target_value = textwrap.dedent(
        f"""\
        import subprocess

        def test_0():
            result = subprocess.run(["{filepath} 0"], stdout=subprocess.PIPE, shell=True)
            return
    """
    )
    out = open(str(filepath).replace(".sh", ".py"), "r")
    assert "".join(out.readlines()) == target_value
    return
