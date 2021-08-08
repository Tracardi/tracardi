from tracardi.service.storage.collection_crud import CollectionCrud


class Sources(list):

    # Persistence
    def bulk(self) -> CollectionCrud:
        return CollectionCrud("source", self)
