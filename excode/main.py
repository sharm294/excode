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

    with open(infile, "r") as f:
        content = f.read()
    if platform.system() == "Linux" or platform.system() == "Darwin":
        target_ending = UNIX_LINE_ENDING
        bad_ending = WINDOWS_LINE_ENDING
    elif platform.system() == "Windows":
        target_ending = WINDOWS_LINE_ENDING
        bad_ending = UNIX_LINE_ENDING
    else:
        raise ValueError("Unsupported platform detected: %s" % platform.system())
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    outfile = infile + ".tmp"
    with open(outfile, "w") as f:
        f.write(content)

    return outfile


# inspired from https://github.com/PyCQA/pylint/blob/master/pylint/utils/pragma_parser.py
MARKDOWN_CONFIG = r"(\[\/\/\]: \# \(.*?\bexcode-config:\s*(.*=.*))\)"
MARKDOWN_VALIDATION = r"\[\/\/\]: \# \(.*?\bexcode-validation:\s*(\d)?\s*([\S\s]*)\)"
MARKDOWN_CODE = r"\`\`\`(.*)\s([^\`]+)\`\`\`"


def extract(infile, filter_str=None):

    infile_2 = change_endings(infile)

    code_blocks = []

    with open(infile_2, "r") as f:
        readfile = f.read()

    options = re.findall(MARKDOWN_CONFIG, readfile)
    if options:
        s = str(options[-1][1])
        extracted = dict(item.split("=") for item in s.split(","))
        extracted["code_blocks"] = []
        extracted["filename"] = infile
    else:
        return {"code_blocks": [], "validation": []}

    options = re.findall(MARKDOWN_CODE, readfile)
    if options:
        for match in options:
            block_metadata = match[0].strip()
            if filter_str and filter_str.strip() not in block_metadata:
                continue
            if "excode" in block_metadata:
                metadata_str = block_metadata.split("excode:")[1]
                metadata = dict(
                    item.strip().split("=") for item in metadata_str.split(",")
                )
            else:
                metadata = {}
            metadata["code"] = match[1]

            if "attach" in metadata:
                if metadata["attach"] == "prev":
                    extracted["code_blocks"][-1]["code"] += metadata["code"]
                else:
                    extracted["code_blocks"][int(metadata["attach"])]["code"].join(
                        metadata["code"]
                    )
            else:
                extracted["code_blocks"].append(metadata)

    if extracted["code_blocks"]:
        extracted["validation"] = [None] * len(extracted["code_blocks"])

        options = re.findall(MARKDOWN_VALIDATION, readfile)
        if options:
            curr_index = 0
            for match in options:
                if match[0]:
                    index = match[0]
                else:
                    index = curr_index
                    curr_index += 1
                extracted["validation"][index] = match[1]

    os.remove(infile_2)  # remove temporary file created by change_endings()

    return extracted


def write_python_function(code_blocks, validation, prefix):
    fun_strings = []
    for k, code_block in enumerate(code_blocks):
        fun_strings.append("")
        fun_strings[-1] += "def {}{}():\n".format(prefix, k)
        fun_strings[-1] += indent(code_block, 4)
        if validation[k]:
            fun_strings[-1] += indent(validation[k], 4)
        fun_strings[-1] += "    return\n"
    return fun_strings


def write_python(outfile, code_blocks, validation, prefix):
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

    with open(outfile, "w") as f:
        if asterisk_imports:
            f.write("\n".join(asterisk_imports))
            f.write("\n\n")

        fun_strings = write_python_function(clean_code_blocks, validation, prefix)
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


def write_bash_wrapper(outfile, num, validation, prefix):
    fun_strings = []
    fun_strings.append("import subprocess")

    filename = os.path.basename(outfile)
    dirname = os.path.dirname(outfile)
    code_blocks = []
    for i in range(num):
        code_blocks.append(
            textwrap.dedent(
                f"""\
                stdout = subprocess.run(["{outfile} {i}"], stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")
                """
            )
        )
    functions = write_python_function(code_blocks, validation, prefix)
    fun_strings.extend(functions)
    python_filepath = str(outfile).replace(".sh", ".py")
    with open(python_filepath, "w") as f:
        f.write("\n\n".join(fun_strings))

    return


def write_bash(outfile, code_blocks, validation, prefix):
    fun_strings = []
    for k, code_block in enumerate(code_blocks):
        fun_strings.append("")
        fun_strings[-1] += "{}{}() {{\n".format(prefix, k)
        fun_strings[-1] += indent(code_block["code"], 4)
        fun_strings[-1] += "}\n"

    fun_strings.extend(write_bash_switch(len(code_blocks), prefix))
    # fun_strings.append("")
    # fun_strings[-1] += "export NUM_TESTS=%s\n" % str(len(code_blocks))
    with open(outfile, "w") as f:
        f.write("\n".join(fun_strings))

    os.chmod(outfile, 0o755)
    write_bash_wrapper(outfile, len(code_blocks), validation, prefix)


def write(outdir, extracted, prefix="test_"):
    code_blocks = extracted["code_blocks"]
    if not code_blocks:
        return None
    validation = extracted["validation"]
    if extracted["mode"] == "python":
        infile = os.path.basename(extracted["filename"]).replace(".md", ".py")
        outfile = os.path.join(outdir, infile)
        write_python(outfile, code_blocks, validation, prefix)
    elif extracted["mode"] == "bash":
        infile = os.path.basename(extracted["filename"]).replace(".md", ".sh")
        outfile = os.path.join(outdir, infile)
        write_bash(outfile, code_blocks, validation, prefix)
    else:
        raise ValueError("unknown language mode")
    return outfile
