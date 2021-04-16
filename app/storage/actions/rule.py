from ... import config
from ...domain.rule import Rule


def upsert_rule(elastic, q, rule: Rule):
    rule_index = config.index['rules']
    rule = {
        '_id': rule.get_id(),
        'uql': q,
        'scope': rule.scope,
        'name': rule.name,
        'description': rule.description,
        'tags': rule.tags,
        'condition': rule.condition,
        'actions': rule.actions
    }
    return elastic.insert(rule_index, [rule])
