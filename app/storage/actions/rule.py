from ... import config
from ...domain.rule import Rule


def upsert_rule(elastic, q, rule: Rule):
    rule_index = config.index['rules']
    segment = {
        '_id': rule.get_id(),
        'uql': q,
        'scope': rule.scope,
        'name': rule.name,
        'description': rule.desc,
        'condition': rule.condition,
        'actions': rule.action
    }
    return elastic.insert(rule_index, [segment])
