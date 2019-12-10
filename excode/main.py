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


# inspired from https://github.com/PyCQA/pylint/blob/master/pylint/utils/pragma_parser.py
MARKDOWN_EXCODE_COMMENT = r"(\s*\[\/\/\]: \# \(.*?\bexcode:\s*(.*=.*))\)"


def extract(f, filter_str=None):

    f = change_endings(f)

    code_blocks = []

    line = f.readline()
    options = re.match(MARKDOWN_EXCODE_COMMENT, line)
    if options:
        s = str(options.group(2))
        extracted = dict(item.split("=") for item in s.split(","))
        extracted["code_blocks"] = []
    else:
        return {"code_blocks": []}

    while True:
        line = f.readline()
        if not line:
            # EOF
            break

        out = re.match("[^`]*```(.*)$", line)
        if out:
            block_metadata = out.group(1).strip()
            if filter_str and filter_str.strip() not in block_metadata:
                continue
            if "excode" in block_metadata:
                metadata_str = block_metadata.split("excode:")[1]
                metadata = dict(
                    item.strip().split("=") for item in metadata_str.split(",")
                )
            else:
                metadata = {}
            metadata["code"] = [f.readline()]
            code_block = []
            while re.search("```", metadata["code"][-1]) is None:
                metadata["code"].append(f.readline())
            metadata["code"] = "".join(metadata["code"][:-1])

            if "attach" in metadata:
                if metadata["attach"] == "prev":
                    extracted["code_blocks"][-1]["code"] += metadata["code"]
                else:
                    extracted["code_blocks"][int(metadata["attach"])]["code"].join(
                        metadata["code"]
                    )
            else:
                extracted["code_blocks"].append(metadata)

    os.remove(f.name)  # remove temporary file created by change_endings()

    return extracted


def write_python_function(code_blocks, prefix):
    fun_strings = []
    for k, code_block in enumerate(code_blocks):
        fun_strings.append("")
        fun_strings[-1] += "def {}{}():\n".format(prefix, k)
        fun_strings[-1] += indent(code_block, 4)
        fun_strings[-1] += "    return\n"
    return fun_strings


def write_python(f, code_blocks, prefix):
    # We'd like to put all code blocks in one file, each in separate test*()
    # functions (for them to be picked up by pytest, for example), but
    # asterisk imports are forbidden in subfunctions. Hence, parse for those
    # imports and put them at the beginning of the output file.
    asterisk_imports = []
    clean_code_blocks = []
    for code_block in code_blocks:
        clean_code_block = []
        for line in code_block["code"].split("\n"):
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

    # fun_strings = []
    # for k, code_block in enumerate(clean_code_blocks):
    #     fun_strings.append("")
    #     fun_strings[-1] += "def {}{}():\n".format(prefix, k)
    #     fun_strings[-1] += indent(code_block, 4)
    #     fun_strings[-1] += "    return\n"
    fun_strings = write_python_function(clean_code_blocks, prefix)
    f.write("\n\n".join(fun_strings))


def write_bash_switch(num, prefix):
    switch = []
    for i in range(num):
        switch.append(
            textwrap.dedent(
                f"""\
                if [[ $1 == {i} ]]; then
                    {prefix}{i}
                fi
                """
            )
        )
    return switch


def write_bash_wrapper(filepath, num, prefix):
    fun_strings = []
    fun_strings.append("import subprocess")

    filename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)
    code_blocks = []
    for i in range(num):
        code_blocks.append(
            f'result = subprocess.run(["{filepath} {i}"], stdout=subprocess.PIPE, shell=True)\n'
        )
    functions = write_python_function(code_blocks, prefix)
    fun_strings.extend(functions)
    python_filepath = filepath.replace(".sh", ".py")
    with open(python_filepath, "w") as f:
        f.write("\n\n".join(fun_strings))

    return


def write_bash(f, code_blocks, prefix):
    fun_strings = []
    for k, code_block in enumerate(code_blocks):
        fun_strings.append("")
        fun_strings[-1] += "{}{}() {{\n".format(prefix, k)
        fun_strings[-1] += indent(code_block["code"], 4)
        fun_strings[-1] += "}\n"

    fun_strings.extend(write_bash_switch(len(code_blocks), prefix))
    # fun_strings.append("")
    # fun_strings[-1] += "export NUM_TESTS=%s\n" % str(len(code_blocks))
    f.write("\n".join(fun_strings))

    filename = f.name
    os.chmod(filename, 0o755)
    write_bash_wrapper(filename, len(code_blocks), prefix)


def write(f, extracted, prefix="test_"):
    code_blocks = extracted["code_blocks"]
    if extracted["mode"] == "python":
        write_python(f, code_blocks, prefix)
    elif extracted["mode"] == "bash":
        write_bash(f, code_blocks, prefix)
    else:
        raise ValueError("unknown language mode")
    return
