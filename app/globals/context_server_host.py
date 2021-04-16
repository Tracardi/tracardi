from ..uql.query.dispatcher import Host

from .. import config
from ..auth.user_db import UserDb

_singleton = None


def get_context_server_host():
    global _singleton

    def get_host():
        user_db = UserDb()
        user = user_db.get_user("karaf")
        username = user['username']
        password = user['password']

        return Host(config.unomi['host'], port=config.unomi['port'], protocol=config.unomi['protocol']).credentials(username, password)

    if _singleton is None:
        _singleton = get_host()

    return _singleton
