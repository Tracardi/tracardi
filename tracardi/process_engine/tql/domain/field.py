class Field:
    def __init__(self, label, value_ref):
        self.label = label
        self.dot = value_ref
        self.value = None

    def _get_value(self):
        if self.value is None:
            self.value = self.dot[self.label]
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
