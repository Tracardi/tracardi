from .create_rule_transformer import CreateRuleTransformer
from .create_segment_transformer import CreateSegmentTransformer
from .delete_transformer import DeleteTransformer
from .select_transformer import SelectTransformer
from .transformer_namespace import TransformerNamespace


class UqlTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_select', SelectTransformer())
        self.namespace('uql_delete', DeleteTransformer())
        self.namespace('url_create_rule', CreateRuleTransformer())
        self.namespace('url_create_segment', CreateSegmentTransformer())

    def start(self, args):
        return args
