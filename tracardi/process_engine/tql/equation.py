from typing import List
from dotty_dict import dotty
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.calc_transformer import CalcTransformer
from tracardi_dot_notation.dot_accessor import DotAccessor

grammar = Parser.read('grammar/math_expr.lark')


class MathEquation:

    def __init__(self, dot: DotAccessor):
        self.dot = dot
        self.parser = Parser(grammar,
                             parser="lalr",
                             transformer=CalcTransformer(dot=self.dot),
                             start='start')

    def evaluate(self, equation: List[str]):
        if isinstance(equation, str):
            equation = [equation]

        results_per_line = []
        for line in equation:
            results_per_line.append(self.parser.parse(line))

        return results_per_line

    def get_variables(self):
        if self.parser.transformer.vars:
            dot = dotty()
            for key, value in self.parser.transformer.vars.items():
                dot[key] = value
            return dot.to_dict()
        return {}
