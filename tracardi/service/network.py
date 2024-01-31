import socket
from typing import Optional

from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


def get_local_ip() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError as e:
        logger.error(str(e))
        return None


local_ip = get_local_ip()
