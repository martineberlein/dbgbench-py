<start> ::= <json>

<json> ::= <value>

<value> ::= <STRING>
         | <NUMBER>
         | <obj>
         | <array>
         | "true"
         | "false"
         | "null"

<obj> ::= "{" <OWS> <pair> <OWS> <more_pairs>* "}"
       | "{" <OWS> "}"

<more_pairs> ::= "," <OWS> <pair> <OWS>

<pair> ::= <STRING> <OWS> ":" <OWS> <value>

<array> ::= "[" <WS> <value> <WS> <more_values>* "]"
         | "[" <OWS> "]"

<more_values> ::= "," <OWS> <value> <OWS>

<STRING> ::= "\"" ( <ESC> | <SAFECODEPOINT> )* "\""

<ESC> ::= "\\" ( <ESC_CHAR> | <UNICODE> )

<ESC_CHAR> ::= "\"" | "\\" | "/" | "b" | "f" | "n" | "r" | "t"

<UNICODE> ::= "u" <HEX> <HEX> <HEX> <HEX>

<HEX> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
       | "a" | "b" | "c" | "d" | "e" | "f"
       | "A" | "B" | "C" | "D" | "E" | "F"

<SAFECODEPOINT> ::= " " | "!" | "#" | "$" | "%" | "&" | "'" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" 
                  | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" 
                  | ":" | ";" | "<" | "=" | ">" | "?" | "@" 
                  | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
                  | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
                  | "[" | "]" | "^" | "_" | "`" 
                  | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m"
                  | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
                  | "{" | "|" | "}" | "~"

<NUMBER> ::= "-"? <INT> ("." <DIGITS>)? <EXP>?

<INT> ::= "0" | <NON_ZERO_DIGIT> <DIGITS>?

<NON_ZERO_DIGIT> ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<DIGITS> ::= <DIGIT>+

<DIGIT> ::= "0" | <NON_ZERO_DIGIT>

<EXP> ::= ("E" | "e") ("+" | "-")? <DIGITS>

<OWS> ::= <WS>*

<WS> ::= " " | "\t" | "\n" | "\r" | ""