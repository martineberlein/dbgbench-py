from lark import Lark, Transformer, ParseTree

class EBNFTransformer(Transformer):
    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)
        self.grammar = dict()
        
    def start(self, items):
        #print(type(items))
        x = "".join(items)
        return f"{{{x}}}" #wtf
    
    def rule(self, items):
        #print(type(items))
        nonterm, expr = items
        return f"\"{nonterm}\" : [ {expr} ],"

    def expr(self, items):
        x = ",".join(items)
        return f"{x}"
    
    def term(self, items):
        x = "".join(items)
        #vllt auch nur ein or?
        #okay wenn "" anzahl mod2 == 0 dann entfernen und ansonsten ....
        if x[0] == "\"" and x[-1] == "\"":
            return x
        else:
            return f"\"{x}\""

    def factor(self, items):
        return items[0]

    def STRING(self, items):
        return "".join(items)
    
    def NONTERMRIGHT(self, items):
        x = "".join(items)
        return x

    def NONTERMLEFT(self, items):
        return "".join(items)
    


ebnf_grammar = """
start: rule+
rule: NONTERMLEFT "::=" expr ";"
expr: term ("|" term)*
term: factor (" " factor | factor)*
factor: NONTERMRIGHT | STRING | "?"
NONTERMLEFT: /<[^<>]+>/
NONTERMRIGHT: /<[^<>]+>/
STRING: /".*"/

%ignore " "
%import common.NEWLINE
%ignore NEWLINE
"""

dict_grammar = """
"""


if __name__ == "__main__":
    with open("src/dbgbench/resources/fandango/find.fan") as f:
        find_fandango_grammar = f.read()
    find_fandango_grammar_test = """
    <start> ::= <filestructure_commands> <find_command>;
    <find_command> ::= <env_variables> <ws> <program> <command> | <program> <command>;
    <program> ::= "timeout 0.5s find";
    <time_zone> ::= "TZ=" <time_zones>;
    """
    parser = Lark(ebnf_grammar, start = "start")
    tree = parser.parse(find_fandango_grammar_test)
    tree: ParseTree
    #print(tree.pretty())
    transformer = EBNFTransformer()
    converted = transformer.transform(tree)
    print(converted)

