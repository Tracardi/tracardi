def validate_list_values(values):
    for value in values:
        if type(value) not in [str, int, float, bool]:
            raise ValueError("Invalid value in list `{}`".format(values))


def append(base, key, value):
    if not isinstance(base, dict):
        raise ValueError("Could not merge value `{}` and values `{}`".format(
            base,
            {key: value}))

    # Treat tuple and set as list
    if key in base:
        if type(base[key]) in [tuple, set]:
            base[key] = list(base[key])
        if isinstance(base[key], list):
            validate_list_values(base[key])

    if type(value) in [set, tuple]:
        value = list(value)
    if isinstance(value, list):
        validate_list_values(value)

    # Merge

    if key not in base:
        base[key] = value
    else:
        """
        Existing value can be only a list or a simple type
        """

        # Existing value is a list
        if isinstance(base[key], list):
            if isinstance(value, list):
                base[key] += value
            else:
                base[key].append(value)
            # Existing value is not a dict and value is a simple value
        elif not isinstance(base[key], dict) and type(value) in [str, int, float, bool, list]:
            base[key] = [base[key]]
            if isinstance(value, list):
                validate_list_values(value)
                base[key] += value
            else:
                base[key].append(value)
        else:
            raise ValueError("Could not merge `{}` with value `{}`".format(base[key], value))

    # make uniq
    if isinstance(base[key], list):
        base[key] = list(set(base[key]))
        if len(base[key]) == 1:
            base[key] = base[key][0]

    return base


def merge(base, dict_list):
    for key in set().union(*dict_list):
        for data in dict_list:
            if key in data:
                # Null
                if data[key] is None:
                    continue
                # Simple types
                elif type(data[key]) in [str, int, float, bool, tuple, list, set]:
                    append(base, key, data[key])
                # Dicts
                elif type(data[key]) in [dict]:
                    if key not in base:
                        base[key] = {}
                    base[key] = merge(base[key], [data[key]])
                # Objects
                elif isinstance(data[key], object):
                    raise ValueError("Object of type `{}: {}` can not be merged with value `{}: {}`".format(
                        key, type(data[key]),
                        key, base[key] if key in base else base))
                else:
                    raise ValueError("Unknown type `{}: {}`".format(key, type(data[key])))

    return base
