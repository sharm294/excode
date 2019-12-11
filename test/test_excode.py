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


def test_plain(get_file, get_out_dir):
    extracted = excode.extract(get_file.join("markdown/test_plain.md"))
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

    filepath = get_out_dir.join("/test_plain.sh")
    excode.write(filepath, extracted)
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
    with open(filepath, "r") as out:
        assert "".join(out.readlines()) == target_value
    return


def test_filter(get_file):
    extracted = excode.extract(
        get_file.join("markdown/test_filter.md"), filter_str="python"
    )
    assert len(extracted["code_blocks"]) == 1
    assert extracted["code_blocks"][0]["code"] == "1 + 2 + 3\n"


def test_shell(get_file, get_out_dir):
    extracted = excode.extract(get_file.join("markdown/test_shell.md"))
    assert len(extracted["code_blocks"]) == 1
    assert extracted["code_blocks"][0]["code"] == "export FOO=bar\n"

    filepath = get_out_dir.join("/test_shell.sh")
    excode.write(filepath, extracted)

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
    with open(filepath, "r") as out:
        assert "".join(out.readlines()) == target_value

    target_value = textwrap.dedent(
        f"""\
        import subprocess

        def test_0():
            result = subprocess.run(["{filepath} 0"], stdout=subprocess.PIPE, shell=True)
            return
        """
    )
    with open(str(filepath).replace(".sh", ".py"), "r") as out:
        assert "".join(out.readlines()) == target_value
