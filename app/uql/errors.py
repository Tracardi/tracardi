class ActionError(ValueError):
    pass


class MappingActionError(ActionError):
    pass


class ActionParamsError(ActionError):
    pass


class ActionParamError(ActionParamsError):
    pass
