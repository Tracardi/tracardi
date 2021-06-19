class FlowStats:

    def __init__(self, triggered=0, errors=None):

        if errors is None:
            errors = []

        self.triggered = triggered
        self.errors = errors

    def __add__(self, other):
        if not isinstance(other, FlowStats):
            raise ValueError("FlowStats can add only other FlowStats. {} given".format(type(other)))

        self.triggered += other.triggered
        self.errors += other.errors

        return self

    def to_json(self):
        return {
                "triggered": self.triggered,
                "errors": self.errors,
        }
