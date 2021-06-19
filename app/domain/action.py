# import logging
# import importlib
# import sys
#
# from pydantic import BaseModel
# from typing import Optional, Tuple, Any
# from abc import ABC, abstractmethod
# from ..domain.profile import Profile
# from .value_object.flow_stats import FlowStats
#
# action_logger = logging.getLogger('Action')
#
#
# class Action(BaseModel):
#     module: str
#     className: str
#     input: Optional[list] = []
#     """
#     input['payload'] = TrackerPayload
#     input['event'] = EventPayload
#     """
#     output: Optional[dict] = {}
#     config: Optional[dict] = {}
#
#     # def load(self) -> 'ActionEvaluator':
#     #     if self.module not in sys.modules:
#     #         module = importlib.import_module(self.module)
#     #     else:
#     #         module = sys.modules[self.module]
#     #
#     #     loaded_class = getattr(module, self.className)
#     #     return loaded_class(self)
#
#     # def prepare_input(self, **kwargs) -> dict:
#     #     valid_params = {}
#     #     for k,v in kwargs.items():
#     #         if k in self.input:
#     #             valid_params[k] = v
#     #     return valid_params
#     #
#     #     # todo evaluate input def from self.action.input and prepare input
#     #
#     # def call(self, **kwargs) -> Tuple[Profile, FlowStats]:
#     #     action_class = self.load()  # type: ActionEvaluator
#     #
#     #     result, stats = action_class.call(**kwargs)
#     #
#     #     action_logger.info("Action `{}.{}({})` executed.".format(
#     #         self.module,
#     #         self.className,
#     #         self.config
#     #     ))
#     #
#     #     return result, stats
#
#     # def run(self, **kwargs):
#     #     params = self.prepare_input(**kwargs)  # todo pass params to call
#     #     return self.call(**params)  # type: Any, FlowStats
#
#
# # class ActionEvaluator(ABC):
# #
# #     def __init__(self, action: Action):
# #         self.action = action
# #
# #     @abstractmethod
# #     def run(self, **kwargs):
# #         pass
# #
# #     def call(self, **kwargs) -> Tuple[Profile, FlowStats]:
# #         stats = FlowStats()
# #
# #         result = self.run(**kwargs)  # type: Profile
# #         stats.triggered += 1
# #
# #         return result, stats
