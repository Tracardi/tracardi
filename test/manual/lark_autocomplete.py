from lark import Lark


schema = r"""
?start: multi_expr
multi_expr: statement 
            | (and_expr|or_expr) ((OR_TERMINAL|AND_TERMINAL) (and_expr|or_expr))*
or_expr: or_multiple_joins
            | or_join
and_expr: and_multiple_joins
            | and_join
or_multiple_joins: (OPEN_BRACKET ( or_join (OR_TERMINAL statement)*) CLOSE_BRACKET)
and_multiple_joins: (OPEN_BRACKET ( and_join (AND_TERMINAL statement)*) CLOSE_BRACKET)

or_join:    (statement|or_multiple_joins|and_multiple_joins) OR_TERMINAL (statement|or_multiple_joins|and_multiple_joins)
and_join:   (statement|or_multiple_joins|and_multiple_joins) AND_TERMINAL (statement|or_multiple_joins|and_multiple_joins)
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

parser = Lark(schema, parser="lalr", debug = True)

interactive = parser.parse_interactive("""
( sa:as or (sd:asa or sds:as) or ddd:as) and sa:as or (as:as or sdsA:s or sd:
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


