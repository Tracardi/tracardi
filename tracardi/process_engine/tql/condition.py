import asyncio

from tracardi.service.singleton import Singleton
from tracardi.service.notation.dot_accessor import DotAccessor

from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer


class Condition(metaclass=Singleton):

    def __init__(self):
        self.parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def parse(self, condition: str):
        try:
            return self.parser.parse(condition)
        except Exception as e:
            raise ValueError(f"Could not parse condition {condition}, details: {str(e)}")

    async def evaluate(self, condition: str, dot: DotAccessor):
        # todo cache tree
        tree = self.parse(condition)
        await asyncio.sleep(0)
        return ExprTransformer(dot=dot).transform(tree)

