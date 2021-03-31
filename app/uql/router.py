from collections import namedtuple

from unomi_query_language.query.transformers.create_rule_transformer import CreateRuleTransformer
from unomi_query_language.query.transformers.create_segment_transformer import CreateSegmentTransformer
from unomi_query_language.query.transformers.delete_transformer import DeleteTransformer
from unomi_query_language.query.transformers.select_transformer import SelectTransformer


class UqlRouter:
    def __init__(self):
        route = namedtuple("Route", "grammar start transformer")

        self.query_mapping = {
            "select": route('uql_select.lark', 'select', SelectTransformer()),
            "create rule": route('uql_create_rule.lark', 'create_rule', CreateRuleTransformer()),
            "create segment": route('uql_create_segment.lark', 'create_segment', CreateSegmentTransformer()),
            "delete": route('uql_delete.lark', 'delete', DeleteTransformer()),
        }

    def __call__(self, *args, **kwargs):
        query = args[0].lower()

        if not query:
            raise ValueError("Could not find route for empty query.")

        for key, route in self.query_mapping.items():
            if key == query[:len(key)]:
                return route
        raise ValueError("Could not find route for query {}".format(query))


if __name__ == "__main__":
    r = UqlRouter()
    x = r("SELECT EVENT")
    print(x)