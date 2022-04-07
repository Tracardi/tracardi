from typing import Dict

from tracardi.domain.console import Console


class StatusLog:
    def __init__(self, time, flow_id, profile_id, origin, class_name, module, type, message):
        self.message = message
        self.type = type
        self.module = module
        self.class_name = class_name
        self.origin = origin
        self.profile_id = profile_id
        self.flow_id = flow_id
        self.time = time

    def is_error(self) -> bool:
        return self.type == 'error'

    def is_warning(self) -> bool:
        return self.type == 'warning'

    def __repr__(self):
        return "{}".format(self.__dict__)


class ConsoleLog(list):

    def get_indexed_event_journal(self) -> Dict[str, StatusLog]:
        return {log.event_id: StatusLog(
            message=log.message,
            type=log.type,
            module=log.module,
            class_name=log.class_name,
            origin=log.origin,
            profile_id=log.profile_id,
            flow_id=log.flow_id,
            time=log.metadata.timestamp
        ) for log in self}

    def get_encoded(self):
        for log in self:  # type: Console
            yield log.encode_record()
