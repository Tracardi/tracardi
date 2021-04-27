from .property_stmt_templates import check_field


def sort_stmt(args, query_data_type):
    # [
    #   ('sort_expr', [('SORT_FIELD', 'version'), ('DIR', 'asc')]),
    #   ('sort_expr', [('SORT_FIELD', 'ala.x'), ('DIR', 'desc')])
    # ]

    if args:
        fields = []
        for _, expr in args:
            field, direction = expr
            field = field[1]
            direction = direction[1]
            query_field = check_field(field, query_data_type)
            if not query_field:
                raise ValueError(
                    "Field or Namespace `{}` is not allowed for data type `{}`.".format(field, query_data_type))
            fields.append("{}:{}".format(query_field, direction.lower()))
        return ",".join(fields)

    return None
