class TracardiException(Exception):
    pass


class StorageException(TracardiException):

    def __init__(self, *args, message=None, details=None):
        TracardiException.__init__(self, *args)
        self.message = message
        self.details = details


class FieldTypeConflictException(TracardiException):

    def __init__(self, *args, rows=None):
        TracardiException.__init__(self, *args)
        if isinstance(rows, list):
            self.details = [row['index']['error']['reason'] for row in rows]
        elif isinstance(rows, str):
            self.details = rows
        else:
            self.details = "Unknown"

    def explain(self):
        if isinstance(self.details, str):
            return self.details
        return ",".join(self.details)


class ExpiredException(TracardiException):
    pass


class UnauthorizedException(TracardiException):
    pass


class BlockedException(TracardiException):
    pass

class InvalidBotTrafficException(TracardiException):
    pass

class WorkflowException(Exception):
    pass


class ConnectionException(TracardiException):

    def __init__(self, *args, response=None):
        TracardiException.__init__(self, *args)
        self.response = response


class LoginException(TracardiException):
    pass


class EventValidationException(TracardiException):
    pass


class DuplicatedRecordException(TracardiException):
    pass
