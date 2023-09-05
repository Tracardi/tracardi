from types import NoneType


class ElasticFieldCondition:
    def __init__(self, field):
        self.field = field

    def __eq__(self, other):
        if isinstance(other, ElasticFieldCondition):
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
                                self.field: other
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
                                    self.field: other
                                }
                            }
                        }
                    }

                query_type = "wildcard" if "*" in other else "term"

                return {
                    query_type: {
                        self.field: {
                            "value": other
                        }
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

            raise ValueError(f"Value is incorrect. Expected type: string, list, Null, or True/False,"
                             f"got {type(other)}.")

    def __ne__(self, other):
        if isinstance(other, ElasticFieldCondition):
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
                    "bool": {
                        "must": {
                            "exists": {
                                self.field: other
                            }
                        }
                    }
                }

            query_type = "term"
            if isinstance(other, str):
                query_type = "wildcard" if "*" in other else "term"

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
