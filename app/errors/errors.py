class NullResponseError(Exception):
    response_status = None


class RecordNotFound(Exception):
    message = None
