from tracardi.process_engine.tql.domain.missing_value import MissingValue


class Field:
    def __init__(self, label, value_ref):
        self.label = label
        self.dot = value_ref

    @property
    def value(self):
        try:
            return self.dot[self.label]
        except KeyError as e:
            return MissingValue(str(e))

    def __eq__(self, other):
        return other == self.value

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other
