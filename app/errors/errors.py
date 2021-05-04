import sys
import traceback


class NullResponseError(Exception):
    response_status = None


class RecordNotFound(Exception):
    message = None


def convert_exception_to_json(e: Exception, custom_type=None):
    return [
        {
            "msg": str(e),
            "type": type(e).__name__ if custom_type is None else custom_type
        }
    ]
