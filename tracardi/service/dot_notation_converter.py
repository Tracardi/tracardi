from dotty_dict import dotty


class DotNotationConverter:

    def __init__(self, profile):
        self.profile = profile
        self.flat_profile = dotty(self.profile.dict())

    def get_profile_file_value_pair(self, dot_notation):
        if dot_notation.startswith('profile@'):
            field = dot_notation[len('profile@'):]
            try:
                return field, self.flat_profile[field]
            except KeyError:
                raise KeyError("Invalid dot notation. Could not find value for `{}` in profile.".format(dot_notation))
        else:
            raise KeyError(
                "Invalid dot notation. Only values from profile are allowed as merge_keys. `{}` "
                "does not start with profile@..".format(dot_notation))


def dotter(data, key='', dots=None):
    if dots is None:
        dots = set()
    if isinstance(data, dict):
        for k in data:
            dotter(data[k], key + '.' + k if key else k, dots)
    else:
        dots.add(key)
    return dots