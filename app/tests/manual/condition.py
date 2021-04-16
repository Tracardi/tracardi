from lark.lark import Lark

p = Lark("""
    expr: and_expr
            | or_expr
    ?and_expr: op_condition
            | "(" expr ")"
            | and_expr " AND "i and_expr
    ?or_expr: op_condition
            | "(" expr ")"
            | or_expr " OR "i or_expr
    ?op_condition: KEY OP NUMBER
    
    OP: /(!=|<=|>=|=>|=<|=|>|<)/
    KEY: /[a-z]/
    
    %import common.NUMBER
""", start='expr', parser='lalr')
t = p.parse(
    "a=1 AND b=2"
)

