class ElasticFieldCondition:
    def __init__(self, field):
        self.field = field

    def __eq__(self, other):
        if isinstance(other, ElasticFieldCondition):
            return {
                "bool": {
                    "filter": {
                        "script": {
                            "script": f"doc['{self.field}'].value ==  doc['{other.field}'].value"
                        }
                    }
                }
            }
        else:
            return {
                "term": {
                    self.field: {
                        "value": other
                    }
                }
            }

    def __gt__(self, other):
        return {
            "range": {
                self.field: {
                    "gt": other
                }
            }
        }

    def __ge__(self, other):
        return {
            "range": {
                self.field: {
                    "gte": other
                }
            }
        }

    def __lt__(self, other):
        return {
            "range": {
                self.field: {
                    "lt": other
                }
            }
        }

    def __le__(self, other):
        return {
            "range": {
                self.field: {
                    "lte": other
                }
            }
        }
