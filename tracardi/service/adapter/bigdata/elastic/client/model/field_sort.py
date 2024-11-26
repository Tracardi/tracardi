class ElasticFieldSort:
    def __init__(self, field: str, order: str = None, format: str = None):
        self.format = format
        self.order = order
        self.field = field

    def to_query(self):
        if self.field is not None and self.order is None and self.format is None:
            return self.field
        elif self.field is not None and self.order is not None:
            output = {
                self.field: {
                    "order": self.order
                }
            }

            if self.format is not None:
                output[self.field]['format'] = self.format

            return output
        else:
            raise ValueError("Invalid ElasticFiledSort.")