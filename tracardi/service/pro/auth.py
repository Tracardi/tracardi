import os

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.driver.elastic import pro as pro_db

_local_path = os.path.dirname(__file__)
logger = get_logger(__name__)


async def get_tpro_token():
    """
    Return None if not configured otherwise returns token.
    """
    try:
        # todo add cache
        result = await pro_db.read_pro_service_endpoint()
    except Exception as e:
        logger.error(f"Exception when reading pro service user data: {str(e)}")
        result = None

    if result is None:
        return None

    return result.token
