from ..mappers.condition_type_mapper import condition_mapper


def check_field(field, data_type):
    # check allowed fields

    allowed_fields = condition_mapper[data_type]['fields']

    if field not in allowed_fields:
        #  maybe it in allowed namespace
        allowed_namespaces = condition_mapper[data_type]['namespaces']
        for namespace in allowed_namespaces:
            if field[:len(namespace)] == namespace:
                return field
        return None

    return allowed_fields[field]


def property_op_stmt(args, query_data_type):

    # find data type. It can be form query of field.
    data_type = args['field']['unomi-type'] if 'unomi-type' in args['field'] else query_data_type

    if query_data_type not in condition_mapper:
        raise ValueError("Unknown data type {} in condition mapper".format(query_data_type))

    unomi_condition_type = condition_mapper[data_type]['condition']

    # check allowed fields

    field = check_field(args['field']['field'], data_type)
    if not field:
        query_field = args['field']['field']
        allowed_fields = list(condition_mapper[data_type]['fields'].keys())
        allowed_namespaces = list(condition_mapper[data_type]['namespaces'].keys())
        raise ValueError(
            "Field or Namespace `{}` is not allowed for data type `{}`. Available fields are {} and namespaces {}".format(
                query_field, data_type, allowed_fields,
                allowed_namespaces))

    result = {
        "type": unomi_condition_type,
        "parameterValues": {
            "propertyName": field,
            "comparisonOperator": args['op']['unomi-op']
        }
    }

    if 'values' in args and args['values'] is not None:
        if isinstance(args['values'], dict):
            args = args['values']
            result["parameterValues"][args['value']['unomi-type']] = args['value']['value']
        elif isinstance(args['values'], list):
            for value in args['values']:
                result["parameterValues"][value['value']['unomi-type']] = value['value']['value']
        else:
            raise ValueError("Unknown value type ``".format())

    return result