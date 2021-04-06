from .. import config
from ..globals.elastic_client import elastic_client


class UserDb:
    def __init__(self):
        self.users_db = [
            {
                "username": config.unomi['username'],
                "password": config.unomi['password'],
                "full_name": "Unomi user",
                "email": "johndoe@example.com",
                "roles": ["unomi"],
                "disabled": False
            }
        ]

    def get_user(self, username):
        for record in self.users_db:
            if record['username'] == username:
                return record
        return None

    def __contains__(self, item):
        return self.get_user(item)


class TokenDb:

    def __init__(self):
        self._elastic = elastic_client()
        self._index = config.index['tokens']

    def __delitem__(self, key):
        self._elastic.delete(self._index, key)

    def __contains__(self, item):
        return self._elastic.exists(self._index, item)

    def __getitem__(self, item):
        return self._elastic.get(self._index, item)

    def __setitem__(self, key, value):
        record = {
            "doc": {"user": value},
            'doc_as_upsert': True
        }
        self._elastic.update(self._index, key, record)


token2user = TokenDb()
