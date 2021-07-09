def flatten(d):
    if d == {}:
        return d
    else:
        k, v = d.popitem()
        if dict != type(v):
            return {k: v, **flatten(d)}
        else:
            flat_kv = flatten(v)
            for k1 in list(flat_kv.keys()):
                flat_kv[str(k) + '.' + str(k1)] = flat_kv[k1]
                del flat_kv[k1]
            return {**flat_kv, **flatten(d)}
