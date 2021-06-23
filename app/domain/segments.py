from app.service.storage.collection_crud import CollectionCrud


class Segments(list):

    # Persistence
    def bulk(self) -> CollectionCrud:
        return CollectionCrud("segment", self)
