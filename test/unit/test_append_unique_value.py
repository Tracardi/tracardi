def _append_value(values, value):
    if not isinstance(values, list):
        values = [values]

    # Append list
    if isinstance(value, list):
        values += value
        # make it unique
        return list(set(values))

    if isinstance(value, set):
        values += list(value)
        # make it unique
        return list(set(values))

    # Append Value
    if value not in values:
        values.append(value)
        return list(set(values))

    return values


def test_append():
    assert set(_append_value(['string1', 'string2'], 'string1')) == {'string1', 'string2'}
    assert set(_append_value(['string1', 'string2'], ['string1'])) == {'string1', 'string2'}
    assert set(_append_value(['string1', 'string2'], {'string1'})) == {'string1', 'string2'}
    assert set(_append_value('string1', {'string1'})) == {'string1'}