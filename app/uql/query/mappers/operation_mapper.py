operation_mapper = {
    'exists': "exists",
    "between": "between",
    "=": "equals",
    "!=": "notEquals",
    "<>": "notEquals",  # todo implement in parser
    '>=': 'greaterThanOrEqualTo',
    '<=': 'lessThanOrEqualTo',
    '>': 'greaterThan',
    '<': 'lessThan',
    'is null': 'isNull',
    'not exists': 'missing',
    'contains': 'contains',
    'notContains': 'not contains',  # todo: implement,
    'startsWith': 'starts with',  # todo: implement,
    'endsWith': 'ends with',  # todo: implement,
    'matchesRegex': 'regex', # todo: implement,
    'in': 'in', # todo: implement,
    'notIn': 'not in', # todo: implement,
    'all': 'has all', # todo: implement,
    'isDay': 'is day', # todo: implement,
    'isNotDay': 'is not day', # todo: implement,

}
