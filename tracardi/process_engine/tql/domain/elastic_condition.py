from types import NoneType


class ElasticFieldCondition:
    def __init__(self, field):
        self.field = field

    @staticmethod
    def _get_field(field):
        return field.field if isinstance(field, ElasticFieldCondition) else field

    def __repr__(self):
        return f"ElasticFieldCondition({self.field})"

    def __eq__(self, other):
        if isinstance(other, ElasticFieldCondition):
            # This is when two fields are compared (field1=field2)
            return {
                "bool": {
                    "filter": {
                        "script": {
                            "script": f"doc['{self.field}'].value == doc['{other.field}'].value"
                        }
                    }
                }
            }
        else:

            if isinstance(other, NoneType):
                return {
                    "bool": {
                        "must_not": {
                            "exists": {
                                "field": self.field
                            }
                        }
                    }
                }

            if isinstance(other, str):
                if other.lower() in ["null", "none", "*"]:
                    return {
                        "bool": {
                            "must_not": {
                                "exists": {
                                    "field": self.field
                                }
                            }
                        }
                    }

                query_type = "wildcard" if "*" in other or "?" in other else "term"

                return {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    self.field: other
                                }
                            },
                            {
                                query_type: {
                                    self.field: {
                                        "value": other
                                    }
                                }
                            },
                            {
                                query_type: {
                                    f"{self.field}.keyword": {
                                        "value": other
                                    }
                                }
                            }
                        ]
                    }
                }

            if isinstance(other, list):
                return {
                    "term": {
                        self.field: {
                            "value": other
                        }
                    }
                }

            if isinstance(other, bool):
                return {
                    "term": {
                        self.field: {
                            "value": other
                        }
                    }
                }

            if isinstance(other, (int, float)):
                return {
                    "term": {
                        self.field: {
                            "value": other
                        }
                    }
                }

            raise ValueError(f"Value is incorrect. Expected type: string, list, Null, or True/False, int, float"
                             f"got {type(other)}.")

    def __ne__(self, other):
        if isinstance(other, ElasticFieldCondition):
            # This is when two fields are compared (field1=field2)
            return {
                "bool": {
                    "filter": {
                        "script": {
                            "script": f"doc['{self.field}'].value != doc['{other.field}'].value"
                        }
                    }
                }
            }

        else:

            if isinstance(other, NoneType):
                return {
                    "exists": {
                        "field": self.field
                    }
                }

            query_type = "term"
            if isinstance(other, str):
                query_type = "wildcard" if "*" in other or "?" in other else "term"

            return {
                "bool": {
                    "must_not": {
                        query_type: {
                            self.field: {
                                "value": other
                            }
                        }
                    }
                }
            }

    def __gt__(self, other):
        #TODO This is when field and value are compared (field1=1). Add field to field comparator
        return {
            "range": {
                self.field: {
                    "gt": self._get_field(other)
                }
            }
        }

    def __ge__(self, other):
        # TODO This is when field and value are compared (field1=1). Add field to field comparator
        return {
            "range": {
                self.field: {
                    "gte": self._get_field(other)
                }
            }
        }

    def __lt__(self, other):
        # TODO This is when field and value are compared (field1=1). Add field to field comparator
        return {
            "range": {
                self.field: {
                    "lt": self._get_field(other)
                }
            }
        }

    def __le__(self, other):
        # TODO This is when field and value are compared (field1=1). Add field to field comparator
        return {
            "range": {
                self.field: {
                    "lte": self._get_field(other)
                }
            }
        }

    def __str__(self):
        return self.field