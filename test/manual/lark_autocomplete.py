from lark import Lark


schema = r"""
?start: multi_expr
multi_expr: expr (OR_TERMINAL|AND_TERMINAL) expr
expr:       statement 
            | or_multiple_joins
            | and_multiple_joins
            | multi_expr
            
or_multiple_joins: (OPEN_BRACKET ( or_join (OR_TERMINAL statement)*) CLOSE_BRACKET)
and_multiple_joins: (OPEN_BRACKET ( and_join (AND_TERMINAL statement)*) CLOSE_BRACKET)

or_join:    statement OR_TERMINAL statement
and_join:   statement AND_TERMINAL statement
statement: FIELD OP (QUOTE VALUE QUOTE | VALUE)
OPEN_BRACKET: "("
CLOSE_BRACKET: ")"
QUOTE:      /[\"]/
VALUE:      /\w+/ 
            | "*"
FIELD:      /\w+/
operator:   ":" 
            | ">=" 
            | "<=" 
            | "<" 
            | ">"
OP: /(:|<=|>=|>|<)/
AND_TERMINAL: /AND/i
OR_TERMINAL: /OR/i
%ignore /\s+/
"""

# AND_TERMINAL: /(\r? \n|\s)+AND(\r? \n|\s)+/i
# OR_TERMINAL: /(\r? \n|\s)+OR(\r? \n|\s)+/i
# or_multiple_joins: (OPEN_BRACKET ( or_join | or_join OR_TERMINAL or_join) CLOSE_BRACKET)

parser = Lark(schema, parser="lalr")

interactive = parser.parse_interactive("""
a:as or (as:a and sas:as) and (sss>1 or d:a or d:a or d:a or d:a ) and sd:as or sad:ass or sdsada:as or ssd:asas

""")
# (s:"d" or d:s or (as:a and d:ss))
# feeds the text given to above into the parsers. This is not done automatically.
interactive.exhaust_lexer()


# returns the names of the Terminals that are currently accepted.
terms = interactive.accepts()

for term in terms:
    for term_def in parser.terminals:
        if term_def.name == term:
            print(term_def.name)
            # print(term_def.pattern.value)


