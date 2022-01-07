from typing import Tuple


class Log:

    def __init__(self, module, class_name, type, message, traceback=None):

        if traceback is None:
            traceback = []

        self.message = message
        self.type = type
        self.class_name = class_name
        self.module = module
        self.traceback = traceback

    def __repr__(self):
        return f"class: {self.class_name}, module: {self.module}, type: {self.type}, message: {self.message}"


class Console:

    def __init__(self, class_name, module):
        self.module = module
        self.class_name = class_name
        self.infos = []
        self.errors = []
        self.warnings = []

    def log(self, item: str):
        self.infos.append(item)

    def error(self, item: str):
        self.errors.append(item)

    def warning(self, item: str):
        self.warnings.append(item)

    def get_logs(self) -> Tuple[Log]:
        for type, logs in zip(["info", "warning", "error"], [self.infos, self.warnings, self.errors]):
            for message in logs:
                yield Log(self.module, self.class_name, type, message)
