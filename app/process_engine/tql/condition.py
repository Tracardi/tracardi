from app.process_engine.tql.parser import Parser
from app.process_engine.tql.transformer.expr_transformer import ExprTransformer


class Condition:
    @staticmethod
    def evaluate(condition, data):
        parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
        tree = parser.parse(condition)
        return ExprTransformer(data=data).transform(tree)
