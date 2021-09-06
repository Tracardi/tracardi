class StorageInfo:

    def __init__(self, index, domain_class_ref, exclude=None, exclude_unset=False):
        self.index = index
        self.domain_class_ref = domain_class_ref
        self.exclude = exclude
        self.exclude_unset = exclude_unset

