from typing import Dict, List

from tracardi.domain.console import Console
from tracardi.service.plugin.domain.console import Log


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


class ConsoleLog(List[Console]):

    def get_indexed_event_journal(self) -> Dict[str, StatusLog]:
        return {
            log.event_id: StatusLog(
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
        for log in self:
            yield log.encode_record()

    def get_errors(self) -> List[dict]:
        return [log.model_dump(mode='json') for log in self if log.is_error()]

    def get_warnings(self) -> List[dict]:
        return [log.model_dump(mode='json') for log in self if log.is_warning()]

    def append_event_log_list(self, event_id: str, flow_id: str, log_list: list):
        for log in log_list:  # type: Log
            console = Console(
                origin="node",
                event_id=event_id,
                flow_id=flow_id,
                profile_id=log.profile_id,
                node_id=log.node_id,
                module=log.module,
                class_name=log.class_name,
                type=log.type,
                message=log.message,
                traceback=log.traceback
            )
            self.append(console)

    def has_errors(self) -> bool:
        for console in self:
            if console.is_error():
                return True

        return False

    def has_warnings(self) -> bool:
        for console in self:
            if console.is_warning():
                return True

        return False
