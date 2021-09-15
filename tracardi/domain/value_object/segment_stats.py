class SegmentStats:

    def __init__(self, triggered=0, errors=None, segments=None):
        if segments is None:
            segments = []
        self.segments = segments
        if errors is None:
            errors = []
        self.triggered = triggered
        self.errors = errors

    def __add__(self, other):
        if not isinstance(other, SegmentStats):
            raise ValueError("SegmentStats can add only other SegmentStats. {} given".format(type(other)))

        self.triggered += other.triggered
        self.errors += other.errors
        self.segments += other.segments

        return self

    def to_json(self):
        return {
            "triggered": self.triggered,
            'errors': self.errors,
            'segments': self.segments
        }
