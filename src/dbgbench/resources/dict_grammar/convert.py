import re

src = """
<start> ::= <printf> <grep_env_var> <program> <command>;
<printf> ::= "printf " <input_> <ws> "|" <ws>;
<command> ::= <cmd_1> <ws> <patterns>;
"""

pattern = re.compile(r"(<[^<>]+>(?:\s*<[^<>]+>)*)|(<[^<>]+>)")
def convert_grammar(src: str):
    src = src.replace("::=", ": [")
    src = src.replace(";", "],")
    src = src.replace("| ", ",")
    return src

# Ersetze die Matches direkt im String
modified_src = pattern.sub(lambda m: f'"{m.group(1).replace(" ", "")}"', src)

modified_src = convert_grammar(modified_src)
print(modified_src)


