import secrets
from ..auth.user_db import token2user, UserDb


class Authentication:

    def __init__(self):
        self.users_db = UserDb()
        self.token2user = token2user

    def authorize(self, username, password):  # username exists
        if not password:
            raise ValueError("Password empty")

        db_username_record = self.users_db.get_user(username)
        if not db_username_record:
            raise ValueError("Incorrect username or password")

        db_username = db_username_record['username']
        db_password = db_username_record['password']
        db_disabled = db_username_record["disabled"]

        if db_disabled:
            raise ValueError("This account was disabled")

        if db_username != username or db_password != password:
            raise ValueError("Incorrect username or password")

        return db_username_record

    @staticmethod
    def _generate_token():
        return secrets.token_hex(32)

    def login(self, username, password):
        user_record = self.authorize(username, password)
        token = self._generate_token()
        # save token, match token with user in token2user
        self.token2user[token] = username

        return {"access_token": token, "token_type": "bearer", "roles": user_record['roles']}

    def logout(self, token):
        del (self.token2user[token])

    def get_user_by_token(self, token):
        return self.token2user[token] if token in self.token2user else None