import re


input_pattern = re.compile(r"^printf '(.*)' \|")


def read_escaped_token(line, pos):
    mode = "NORMAL"
    cp = pos+1
    while cp < len(line):
        if line[cp] == "'" and "NORMAL" == mode:
            return line[pos:cp+1], cp+1
        elif mode == "ESCAPED":
            mode = "NORMAL"
        elif line[cp] == "\\" and "NORMAL" == mode:
            mode = "ESCAPED"
        cp = cp + 1
    raise AssertionError("Missing closing quotation.")


def read_unescaped_token(line, pos):
    end = line.find(" ", pos)
    if -1 == end:
        return line[pos:], len(line)
    return line[pos:end], end


def split_cli(line):
    pos = 0
    while pos < len(line):
        if '\'' == line[pos]:
            token, pos = read_escaped_token(line, pos)
            yield token
        elif ' ' == line[pos]:
            pos = pos + 1
        else:
            token, pos = read_unescaped_token(line, pos)
            yield token


def split_grep_line(cli):
    match = re.match(input_pattern, cli)
    if match is None:
        start = 0
    else:
        start = match.end()
    stop = cli.find("timeout 1s grep", start)
    env = cli[start:stop]
    command = split_cli(cli[stop+16:])
    return env, list(command)


def identify_pattern(command):
    for i in range(0, len(command)):
        token = command[i]
        if token.startswith("'") and not token.startswith("'-"):
            return i
    raise AssertionError("There does not seem to be a pattern!")


class PrefixWriter:

    def __init__(self, writer, prefix):
        self.__writer = writer
        self.__prefix = prefix
        self.__remainder = ""

    def write(self, text):
        for line in text.splitlines(keepends=True):
            if line.endswith("\n"):
                self.__writer.write(self.__prefix + self.__remainder + line)
                self.__remainder = ""
            else:
                self.__remainder = self.__remainder + line

    def close(self):
        if 0 != len(self.__remainder):
            self.__writer.write(self.__prefix + self.__remainder)
            self.__remainder = ""
        self.__writer.close()

    def flush(self):
        if 0 != len(self.__remainder):
            self.__writer.write(self.__prefix + self.__remainder)
            self.__remainder = ""
        self.__writer.flush()

