import json
import os

from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Predefined {file_path} exists but could not be parsed as JSON file. Details: {str(e)}")
            return None
    else:
        return None
