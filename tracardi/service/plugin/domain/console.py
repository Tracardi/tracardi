from typing import Tuple


class Log:

    def __init__(self, module: str, class_name: str, type: str, message: str, flow_id: str = None,
                 profile_id: str = None, node_id: str = None, traceback=None):
        if traceback is None:
            traceback = []

        self.message = message
        self.type = type
        self.class_name = class_name
        self.module = module
        self.node_id = node_id
        self.profile_id = profile_id
        self.flow_id = flow_id
        self.traceback = traceback

    def __repr__(self):
        return f"Node: {self.node_id}, class: {self.class_name}, module: {self.module}, " \
               f"type: {self.type}, message: {self.message}"


class ConsoleStatus:
    errors = 0
    warnings = 0
    infos = 0


class Console:

    def __init__(self, class_name, module, flow_id=None, profile_id=None, node_id=None):
        self.module = module
        self.class_name = class_name
        self.infos = []
        self.errors = []
        self.warnings = []
        self.node_id = node_id
        self.flow_id = flow_id
        self.profile_id = profile_id

    def log(self, item: str):
        self.infos.append(item)

    def error(self, item: str):
        self.errors.append(item)

    def warning(self, item: str):
        self.warnings.append(item)

    def get_logs(self) -> Tuple[Log]:
        for type, logs in zip(["info", "warning", "error"], [self.infos, self.warnings, self.errors]):
            for message in logs:
                yield Log(self.module,
                          self.class_name,
                          type,
                          message,
                          profile_id=self.profile_id,
                          flow_id=self.flow_id,
                          node_id=self.node_id)

    def get_status(self) -> ConsoleStatus:
        status = ConsoleStatus()
        status.errors = len(self.errors)
        status.warnings = len(self.warnings)
        status.infos = len(self.infos)
        return status

    def __repr__(self):
        return f"Class: {self.class_name}, Errors: {self.errors}, Warnings: {self.warnings}, Infos: {self.infos}"

    def dict(self):
        return {
            "infos": self.infos,
            "errors": self.errors,
            "warnings": self.warnings
        }

    def append(self, data):
        self.infos = data['infos']
        self.errors = data['errors']
        self.warnings = data['warnings']
