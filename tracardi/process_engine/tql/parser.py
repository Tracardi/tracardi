import os
from lark import Lark

_local_dir = os.path.dirname(__file__)


class Parser:

    def __init__(self, grammar, start, parser='earley', transformer=None):
        import_paths = [
            os.path.join(_local_dir, 'grammar')
        ]
        self.transformer = transformer
        self.base_parser = Lark(grammar,
                                start=start,
                                parser=parser,
                                transformer=self.transformer,
                                import_paths=import_paths)

    @staticmethod
    def read(file):
        with open(os.path.join(_local_dir, file)) as f:
            return f.read()

    def parse(self, query: str):
        return self.base_parser.parse(query)

    def next(self, query):
        interactive = self.base_parser.parse_interactive(query)

        # feeds the text given to above into the parsers. This is not done automatically.
        interactive.exhaust_lexer()

        # returns the names of the Terminals that are currently accepted.
        print(interactive.accepts())

