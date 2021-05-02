from pprint import pprint
from ..uql.query.parser import Parser
from ..uql.query.grammar.grammars import read
from ..uql.query.transformers.create_rule_transformer import CreateRuleTransformer


def test_regular_create_rule():
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
    assert body['metadata']['tags'] == ['tag1', 'tag2']

    assert body['condition']['type'] == 'eventPropertyCondition'
    assert body['condition']['parameterValues']['comparisonOperator'] == 'equals'
    assert body['condition']['parameterValues']['propertyName'] == 'eventType'
    assert body['condition']['parameterValues']['propertyValue'] == 'event'

    assert body == {
        "actions": [
            {
                "parameterValues": {
                    "setPropertyName": "properties(a)",
                    "setPropertyStrategy": "addValue",
                    "setPropertyValue": "1"
                },
                "type": "setPropertyAction"
            },
            {
                "parameterValues": {
                    "setPropertyName": "properties(a)",
                    "setPropertyStrategy": "alwaysSet",
                    "setPropertyValue": "1"
                },
                "type": "setPropertyAction"
            }
        ],
        "condition": {
            "parameterValues": {
                "comparisonOperator": "equals",
                "propertyName": "eventType",
                "propertyValue": "event"
            },
            "type": "eventPropertyCondition"
        },
        "itemId": "name",
        "itemType": "rule",
        "metadata": {
            "description": "description",
            "enabled": True,
            "hidden": False,
            "id": "name",
            "missingPlugins": False,
            "name": "name",
            "readOnly": False,
            "scope": "scope",
            "tags": [
                "tag1",
                "tag2"
            ]
        },
        "priority": -1,
        "raiseEventOnlyOnceForProfile": False,
        "raiseEventOnlyOnceForSession": False
    }


def test_boolean_create_rule():
    p = Parser(read('uql_create_rule.lark'), start='create_rule')
    t = p.parse(
        """
        CREATE RULE 
        "name" 
        DESCRIBE "description"
        IN SCOPE "scope" 
        WHEN event:type="identify" AND event:scope = "scope"  
        THEN profile.CopyAll()
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

    assert body == {
        "actions": [
            {
                "parameterValues": {},
                "type": "allEventToProfilePropertiesAction"
            }
        ],
        "condition": {
            "parameterValues": {
                "operator": "and",
                "subConditions": [
                    {
                        "parameterValues": {
                            "comparisonOperator": "equals",
                            "propertyName": "eventType",
                            "propertyValue": "identify"
                        },
                        "type": "eventPropertyCondition"
                    },
                    {
                        "parameterValues": {
                            "comparisonOperator": "equals",
                            "propertyName": "scope",
                            "propertyValue": "scope"
                        },
                        "type": "eventPropertyCondition"
                    }
                ]
            },
            "type": "booleanCondition"
        },
        "itemId": "name",
        "itemType": "rule",
        "metadata": {
            "description": "description",
            "enabled": True,
            "hidden": False,
            "id": "name",
            "missingPlugins": False,
            "name": "name",
            "readOnly": False,
            "scope": "scope",
            "tags": []
        },
        "priority": -1,
        "raiseEventOnlyOnceForProfile": False,
        "raiseEventOnlyOnceForSession": False
    }
