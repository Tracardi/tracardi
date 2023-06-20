from tracardi.service.storage.index import Index


def get_entity_index(index: Index):
    if not index.multi_index:
        # This function does not work on aliases
        return index
    return index.get_index_alias()
