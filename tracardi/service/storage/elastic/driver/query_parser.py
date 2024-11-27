from typing import Optional
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.singleton import Singleton
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.filter_transformer import FilterTransformer

_logger = get_logger(__name__)

class SqlSearchQueryParser(metaclass=Singleton):
    def __init__(self):
        self.parser = Parser(Parser.read('grammar/filter_condition.lark'), start='expr')

    def parse(self, query) -> Optional[dict]:
        if not query:
            return None

        tree = self.parser.parse(query)
        result = FilterTransformer().transform(tree)
        return result