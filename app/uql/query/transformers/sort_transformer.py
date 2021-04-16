from .common_transformer import CommonTransformer
from .transformer_namespace import TransformerNamespace


class SortTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace("uql_common__", CommonTransformer())

    def sort(self, args):
        if not isinstance(args, list):
            args = [args]

        return args

    def SORT_FIELD(self, args):
        return 'SORT_FIELD', args.value

    def DIR(self, args):
        return 'DIR', args.lower()

    def sort_expr(self, args):
        return 'sort_expr', args

