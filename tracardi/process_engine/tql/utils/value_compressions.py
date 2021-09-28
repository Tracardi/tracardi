from tracardi.process_engine.tql.domain.operations import OrOperation, AndOperation


class Values:

    def __init__(self):
        self.values = []

    def append_or_value(self, value):
        if isinstance(value, OrOperation):
            self.values = self.values + value['bool']['should']
        else:
            self.values.append(value)

    def append_and_value(self, value):
        if isinstance(value, AndOperation):
            self.values = self.values + value['bool']['must']
        else:
            self.values.append(value)
