from .property_stmt_templates import property_op_stmt


def nested_condition_stmt(condition_args, query_data_type):
    for type, args in condition_args:
        if type == 'CONDITION' and args:
            return property_op_stmt(args, query_data_type)

        if type == 'BOOLEAN-CONDITION' and args:
            return boolean_condition_stmt(args, query_data_type)


def boolean_condition_stmt(args, query_data_type):
    return {
        "type": "booleanCondition",
        "parameterValues": {
            "operator": args['bool'],
            "subConditions": [nested_condition_stmt([sub_args], query_data_type) for sub_args in args['subConditions']]
        }
    }


def match_all_condition_stmt():
    return {
        "type": "matchAllCondition",
        "parameterValues": {}
    }
