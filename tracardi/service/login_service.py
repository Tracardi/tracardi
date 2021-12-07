from tracardi.domain.user import User
from tracardi.service.storage.driver import storage
from tracardi.service.sha1_hasher import SHA1Encoder
from tracardi.exceptions.exception import LoginException


async def find_user(username: str, password: str) -> User:
    result = (await storage.driver.user.get_by_login_data(
        username=username,
        password=password
    ))
    if result is None:
        raise LoginException("Incorrect username or password.")
    return result
