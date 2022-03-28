from tracardi.process_engine.tql.domain.missing_value import MissingValue


class Field:
    def __init__(self, label, value_ref):
        self.label = label
        self.dot = value_ref
        self.value = None

    def _get_value(self):
        if self.value is None:
            try:
                value = self.dot[self.label]
                # If value did not change that means it does not exist.
                if value == self.label:
                    self.value = None
                else:
                    self.value = value
            except KeyError as e:
                return MissingValue(str(e))
        return self.value

    def __eq__(self, other):
        return other == self._get_value()

    def __gt__(self, other):
        return self._get_value() > other

    def __ge__(self, other):
        return self._get_value() >= other

    def __lt__(self, other):
        return self._get_value() < other

    def __le__(self, other):
        return self._get_value() <= other
