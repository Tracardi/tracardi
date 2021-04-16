from ....errors import MappingActionError
from ..action_mapper import action_mapper


class ActionController:
    def __init__(self):
        self._action_mapper = action_mapper

    def run(self, item):
        if item not in self._action_mapper:
            raise MappingActionError(
                "Invalid action function {}. Available action functions {}".format(item,
                                                                                   list(self._action_mapper.keys())))

        return self._action_mapper[item]['exec']


action_controller = ActionController()
