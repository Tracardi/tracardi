from .common_transformer import CommonTransformer
from .transformer_namespace import TransformerNamespace


class FunctionTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace("uql_common__", CommonTransformer())

    def function(self, args):
        return 'FUNCTION', args

    def FUNCTION_NAME(self, args):
        return 'FUNCTION_NAME', args.value

    def params(self, args):
        return 'PARAMS', args

    def value(self, args):
        return args[0]
