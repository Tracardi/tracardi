import asyncio

from tracardi.process_engine.tql.transformer.filter_transformer import FilterTransformer
from tracardi.service.singleton import Singleton
from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi.process_engine.tql.parser import Parser


class FilterCondition(metaclass=Singleton):

    def __init__(self):
        self.parser = Parser(Parser.read('grammar/filter_condition.lark'), start='expr')

    def parse(self, condition):
        return self.parser.parse(condition)

    async def evaluate(self, condition, dot: DotAccessor):
        # todo cache tree
        tree = self.parse(condition)
        await asyncio.sleep(0)
        return FilterTransformer(dot=dot).transform(tree)
