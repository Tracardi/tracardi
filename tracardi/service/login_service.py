from tracardi.domain.user import User
from tracardi.service.storage.driver import storage
from tracardi.exceptions.exception import LoginException


async def find_user(email: str, password: str) -> User:
    result = await storage.driver.user.get_by_credentials(
        email=email,
        password=password
    )
    if result is None:
        await storage.driver.user_log.add_log(email=email, successful=False)
        raise LoginException("Incorrect username or password.")
    else:
        await storage.driver.user_log.add_log(email=email, successful=True)
        return result
