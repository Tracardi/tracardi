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
        self.details = [row['index']['error']['reason'] for row in rows]

    def explain(self):
        return ",".join(self.details)


class ExpiredException(TracardiException):
    pass


class UnauthorizedException(TracardiException):
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
