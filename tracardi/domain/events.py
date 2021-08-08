from tracardi.service.storage.collection_crud import CollectionCrud


class Events(list):

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("event", self)
