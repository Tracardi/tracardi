from dotty_dict import dotty


class DotNotationConverter:

    def __init__(self, profile):
        self.profile = profile

    def get_profile_fiel_value_pair(self, dot_notation):
        if dot_notation.startswith('profile@'):
            field = dot_notation[len('profile@'):]
            dot = dotty(self.profile.dict())
            try:
                return field, dot[field]
            except KeyError:
                raise KeyError("Invalid dot notation. Could not find value for `{}` in profile.".format(dot_notation))
        else:
            raise KeyError(
                "Invalid dot notation. Only values from profile are allowed as merge_keys. `{}` does not start with profile@..".format(
                    dot_notation))