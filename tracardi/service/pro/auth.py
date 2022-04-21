import logging
import os

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage

_local_path = os.path.dirname(__file__)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def get_tpro_token():
    """
    Return None if not configured otherwise returns token.
    """
    try:
        # todo add cache
        result = await storage.driver.pro.read_pro_service_endpoint()
    except Exception as e:
        logger.error(f"Exception when reading pro service user data: {str(e)}")
        result = None

    if result is None:
        return None

    return result.token
