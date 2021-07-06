candidates = dict()
path = []


def append(base, key, value):
    if not isinstance(base, dict):
        raise ValueError("Expected dict but got {}".format(base))

    if key not in base:
        base[key] = value
    elif isinstance(base[key], set):
        base[key] += list(base[key]) + value
    elif isinstance(base[key], list):
        base[key] += value
    else:
        base[key] = [base[key]]
        if isinstance(value, list):
            base[key] += value
        else:
            base[key].append(value)

    # make uniq
    if isinstance(base[key], list):
        base[key] = list(set(base[key]))
    return base


def merge_dictionary_list(base, dict_list):
    for key in set().union(*dict_list):
        for data in dict_list:
            if key in data:
                if type(data[key]) in [str, int, float, list, set]:
                    if not isinstance(base, dict):
                        raise ValueError("Could not merge value `{}` and values `{}`".format(base, dict_list))
                    append(base, key, data[key])
                elif type(data[key]) in [dict]:
                    if key not in base:
                        base[key] = {}
                    base[key] = merge_dictionary_list(base[key], [data[key]])
                else:
                    print(key, data[key])
    return base


# def merge_candidates(dict_list):
#     return {
#       k: [d.get(k) for d in dict_list if k in d] # explanation A
#       for k in set().union(*dict_list) # explanation B
#     }

a = {
    "a": 1,
    "b": [1, 2],
    "c": None,
    "f": {"a": 1},
    "g": {"a": 1},
    "conflict": {"ccc": 1}
}

b = {
    "a": "2",
    "b": "3",
    # "c": 1,
    "d": 1,
    "e": [1, 2],
    "f": {
        "b": 1
    },
    "c": {"aaa": 1},
    "g": {"a": ["1", 2]},
    "conflict": "a",
}

c = merge_dictionary_list(candidates, [a, b])
# d = merge_candidates([a, b])
print(c)
# print(d)
