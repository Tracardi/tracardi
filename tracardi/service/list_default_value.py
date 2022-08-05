def list_value_at_index(data, index, default_value):
    if index < len(data):
        r = data[index]
    else:
        r = default_value
        data.append(r)

    return r, data

