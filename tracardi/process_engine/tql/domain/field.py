class Field:
    def __init__(self, label, value):
        self.label = label
        self.value = value

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
