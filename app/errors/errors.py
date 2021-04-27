import sys
import traceback


class NullResponseError(Exception):
    response_status = None


class RecordNotFound(Exception):
    message = None


def convert_exception_to_json(e: Exception):
    return [
        {
            "msg": str(e),
            "type": type(e).__name__
        }
    ]
