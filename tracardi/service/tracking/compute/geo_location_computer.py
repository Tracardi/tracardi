from typing import Optional

from pydantic import ValidationError

from tracardi.domain.geo import Geo
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


def get_geo_location(context: dict) -> Optional[Geo]:
    if 'location' in context:

        try:
            return Geo(**context['location'])

        except ValidationError as e:
            logger.error(str(e))

    return None
