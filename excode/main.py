# -*- coding: utf-8 -*-
#
import os
import platform
import re

# https://stackoverflow.com/a/8348914/353337
try:
    import textwrap

    textwrap.indent
except AttributeError:  # undefined function (wasn't added until Python 3.3)

    def indent(text, amount, ch=" "):
        padding = amount * ch
        return "".join(padding + line for line in text.splitlines(True)).replace(
            "\n    \n", "\n\n"
        )


else:

    def indent(text, amount, ch=" "):
        return textwrap.indent(text, amount * ch).replace("\n    \n", "\n\n")


def change_endings(infile):
    """
    Sometimes, READMEs get weird file endings. We force the endings appropriate
    to the platform in case they're wrong. Otherwise, there's no change made.

    Args:
        infile (file): The open file object for the source README file

    Raises:
        ValueError: Raised if platform cannot be determined

    Returns:
        file: The open file object with the fixed endings
    """
    WINDOWS_LINE_ENDING = "\r\n"
    UNIX_LINE_ENDING = "\n"

    content = infile.read()
    if platform.system() == "Linux" or platform.system() == "Darwin":
        target_ending = UNIX_LINE_ENDING
        bad_ending = WINDOWS_LINE_ENDING
    elif platform.system() == "Windows":
        target_ending = WINDOWS_LINE_ENDING
        bad_ending = UNIX_LINE_ENDING
    else:
        raise ValueError("Unsupported platform detected: %s" % platform.system())
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    outfile = infile.name + ".tmp"
    with open(outfile, "w+") as f:
        f.write(content)

    return open(outfile)


def extract(f, filter_str=None):

    f = change_endings(f)

    code_blocks = []
    while True:
        line = f.readline()
        if not line:
            # EOF
            break

        out = re.match("[^`]*```(.*)$", line)
        if out:
            if filter_str and filter_str.strip() != out.group(1).strip():
                continue
            code_block = [f.readline()]
            while re.search("```", code_block[-1]) is None:
                code_block.append(f.readline())
            code_blocks.append("".join(code_block[:-1]))
    os.remove(f.name)  # remove temporary file created by change_endings()
    return code_blocks


def write(f, code_blocks, mode, prefix="test"):
    if mode == "python":
        # We'd like to put all code blocks in one file, each in separate test*()
        # functions (for them to be picked up by pytest, for example), but
        # asterisk imports are forbidden in subfunctions. Hence, parse for those
        # imports and put them at the beginning of the output file.
        asterisk_imports = []
        clean_code_blocks = []
        for code_block in code_blocks:
            clean_code_block = []
            for line in code_block.split("\n"):
                if re.match("\\s*from\\s+[^\\s]+\\s+import\\s+\\*", line):
                    asterisk_imports.append(line)
                else:
                    clean_code_block.append(line)
            clean_code_blocks.append("\n".join(clean_code_block))
        # make list unique
        asterisk_imports = list(set(asterisk_imports))

        if asterisk_imports:
            f.write("\n".join(asterisk_imports))
            f.write("\n\n")

        fun_strings = []
        for k, code_block in enumerate(clean_code_blocks):
            fun_strings.append("")
            fun_strings[-1] += "def {}{}():\n".format(prefix, k)
            fun_strings[-1] += indent(code_block, 4)
            fun_strings[-1] += "    return\n"
        f.write("\n\n".join(fun_strings))

    elif mode == "bash":
        fun_strings = []
        for k, code_block in enumerate(code_blocks):
            fun_strings.append("")
            fun_strings[-1] += "{}{} (){{\n".format(prefix, k)
            fun_strings[-1] += indent(code_block, 4)
            fun_strings[-1] += "}\n"

        fun_strings.append("")
        fun_strings[-1] += "export NUM_TESTS=" + str(len(code_blocks))
        f.write("\n\n".join(fun_strings))
    else:
        raise Exception("unknown language mode")
    return
