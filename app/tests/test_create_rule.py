from pprint import pprint
from ..uql.query.parser import Parser
from ..uql.query.grammar.grammars import read
from ..uql.query.transformers.create_rule_transformer import CreateRuleTransformer


def test_create_rule():
    p = Parser(read('uql_create_rule.lark'), start='create_rule')
    t = p.parse(
        """
        CREATE RULE 
            WITH TAGS ["tag1","tag2"] 
            "name" 
            DESCRIBE "description"
            IN SCOPE "scope" 
            WHEN eventType="event"
            THEN 
                profile.AddStringToList(a,"1"), profile.SetString(a,"1")
        """
    )

    query = CreateRuleTransformer().transform(t)
    pprint(query)

    assert len(query) == 5

    type, url, method, body, code = query

    assert type == 'rule'
    assert url == 'cxs/rules/'
    assert method == 'POST'
    assert code == 204

    assert 'actions' in body
    assert 'condition' in body
    assert 'metadata' in body
    assert 'itemId' in body
    assert 'itemType' in body
    assert 'priority' in body
    assert 'raiseEventOnlyOnceForProfile' in body
    assert 'raiseEventOnlyOnceForSession' in body

    assert body['metadata']['description'] == 'description'
    assert body['metadata']['enabled'] == True
    assert body['metadata']['hidden'] == False
    assert body['metadata']['id'] == 'name'
    assert body['metadata']['missingPlugins'] == False
    assert body['metadata']['readOnly'] == False
    assert body['metadata']['scope'] == 'scope'
    assert body['metadata']['tags'] == ['tag1','tag2']

    assert body['condition']['type'] == 'eventPropertyCondition'
    assert body['condition']['parameterValues']['comparisonOperator'] == 'equals'
    assert body['condition']['parameterValues']['propertyName'] == 'eventType'
    assert body['condition']['parameterValues']['propertyValue'] == 'event'