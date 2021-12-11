from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi.process_engine.tql.transformer.transformer_namespace import TransformerNamespace
from lark import v_args, Token


@v_args(inline=True)
class CalcTransformer(TransformerNamespace):
    from operator import add, sub, mul, truediv as div, neg

    number = float

    def __init__(self, dot, *args, **kwargs):
        if not isinstance(dot, DotAccessor):
            raise ValueError("Data passed to ExprTransformer must be type of DotAccessor.")
        super().__init__(*args, **kwargs)
        # self.namespace('uql_function__', FunctionTransformer())
        self._dot = dot
        self.vars = {}

    def assign_var(self, *args):
        token, value = args
        if token.type == "NAME":
            self.vars[token.value] = value
        elif token.type == "FIELD":
            self._dot[token.value] = value
        return value

    def field(self, field):
        value = self._dot[field]
        if isinstance(value, str):
            try:
                value = float(value)
            except Exception:
                raise ValueError(f"Field `{field}` is a string. System tried to parse it into number, but it failed.")

        if isinstance(value, float) or isinstance(value, int):
            return value

        raise ValueError(f"Field `{field}` is not a number it is a `{type(field)}`.")

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception(f"Variable `{name}` not found")
