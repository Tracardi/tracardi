class IndexMapping:

    def __init__(self, mapping):
        self.mapping = mapping
        self.field_collection = {}

    def _flatten_dict(self, data, keystring=''):
        if isinstance(data, dict) and len(data) > 0:
            keystring = keystring + '.' if keystring else keystring
            for k in data:
                yield from self._flatten_dict(data[k], keystring + str(k))
        else:
            yield keystring, data

    def get_field_names(self):
        for index, mapping in self.mapping.items():
            self._get_field_names(mapping['mappings'], self.field_collection)
        return [k for k, v in self._flatten_dict(self.field_collection) if k != ""]

    def _get_field_names(self, mapping, collection):
        for data, fields in mapping.items():
            if data == 'properties':
                for field in fields.keys():
                    collection[field] = {}
                    self._get_field_names(fields[field], collection[field])
