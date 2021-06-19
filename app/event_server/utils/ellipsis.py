def replace_with_ellipsis(dictionary, key, value=...):
    return {k: replace_with_ellipsis(value if v == key else v, key, value)
            for k,v in dictionary.items()} if isinstance(dictionary, dict) else dictionary
