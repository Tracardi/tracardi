from .. import config


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


token2user = {}
