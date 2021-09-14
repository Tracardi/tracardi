class TracardiException(Exception):
    pass


class StorageException(TracardiException):
    pass


class ExpiredException(TracardiException):
    pass


class UnauthorizedException(TracardiException):
    pass


