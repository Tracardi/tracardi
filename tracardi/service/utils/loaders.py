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


def pre_config_file_loader(file_path):
    content = load_json(file_path)
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Predefined {file_path} exists but could not be parsed as JSON file. Details: {str(e)}")
            return None
    logger.info(f"Preconfiguration file `{file_path}` loaded with {len(content) if content else 'no'} definitions.")
    return content
