from app.process_engine.tql.parser import Parser
from app.process_engine.tql.transformer.expr_transformer import ExprTransformer


class Condition:

    @staticmethod
    def parse(condition):
        parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
        return parser.parse(condition)

    @staticmethod
    def evaluate(condition, data):
        tree = Condition.parse(condition)
        return ExprTransformer(data=data).transform(tree)

