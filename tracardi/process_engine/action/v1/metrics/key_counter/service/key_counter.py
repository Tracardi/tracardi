from typing import Union


class KeyCounter:

    def __init__(self, counts: dict):
        if not isinstance(counts, dict):
            raise ValueError("Storage path for key counting must be dict.")
        self.counts = counts

    def _increase(self, key, increase_value: Union[float,int] = 1):
        if key not in self.counts:
            self.counts[key] = 0
        self.counts[key] += increase_value

    def count(self, key):
        if not isinstance(key, list) and not isinstance(key, str) and not isinstance(key, dict):
            raise ValueError("Keys to count must be either list of strings or string {} given".format(type(key)))

        if isinstance(key, list):
            for k in key:
                if isinstance(k, dict):
                    for _k, _v in k.items():
                        if isinstance(_v, int) or isinstance(_v, float):
                            self._increase(_k, _v)
                else:
                    self._increase(k)
        elif isinstance(key, dict):
            for k, v in key.items():
                if isinstance(v, int) or isinstance(v, float):
                    self._increase(k, v)
        else:
            self._increase(key)
