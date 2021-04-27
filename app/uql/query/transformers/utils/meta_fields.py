class MetaFields:
    def __init__(self, elements):
        self.elements = elements

    def get_read_only(self):
        return self.elements['READ_ONLY'] if 'READ_ONLY' in self.elements else False

    def get_hidden(self):
        return self.elements['HIDDEN'] if 'HIDDEN' in self.elements else False

    def get_disabled(self):
        return self.elements['DISABLED'] if 'DISABLED' in self.elements else True

    def get_descride(self):
        return self.elements['DESCRIBE'] if 'DESCRIBE' in self.elements else ""

    def get_name(self):
        return self.elements['NAME'] if 'NAME' in self.elements else None

    def get_tags(self):
        return self.elements['TAGS'] if 'TAGS' in self.elements else []

    def get_in_scope(self):
        return self.elements['IN_SCOPE'] if 'IN_SCOPE' in self.elements else None
