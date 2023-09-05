schema = r"""
?start: multi_expr
multi_expr: statement 
            | (and_expr|or_expr) ((OR|AND) (and_expr|or_expr))*
or_expr: or_multiple_joins
            | or_join
and_expr: and_multiple_joins
            | and_join
or_multiple_joins: (OPEN_BRACKET ( or_join (OR statement)*) CLOSE_BRACKET)
and_multiple_joins: (OPEN_BRACKET ( and_join (AND statement)*) CLOSE_BRACKET)

or_join:    (statement|or_multiple_joins|and_multiple_joins) OR (statement|or_multiple_joins|and_multiple_joins)
and_join:   (statement|or_multiple_joins|and_multiple_joins) AND (statement|or_multiple_joins|and_multiple_joins)
statement: FIELD OP (QUOTE VALUE QUOTE | VALUE)
OPEN_BRACKET: "("
CLOSE_BRACKET: ")"
QUOTE:      /[\"]/
VALUE:      /[^\s\"]+|(?<!\\)[\"](.*?)(?<!\\)[\"]/ 
            | "*"
FIELD:      /[a-zA-z_\.-0-9]+/
SPACE:      /[\s]+/
operator:   ":" 
            | ":>=" 
            | ":<=" 
            | ":<" 
            | ":>"
OP: /(:|:<=|:>=|:>|:<)/
AND: /AND/i
OR: /OR/i

%ignore /\s+/
"""