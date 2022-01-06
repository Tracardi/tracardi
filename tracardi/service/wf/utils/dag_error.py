class DagGraphError(ValueError):
    pass


class DagError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.port = kwargs['port'] if 'port' in kwargs else None
        self.input = kwargs['input'] if 'input' in kwargs else None
        self.edge = kwargs['edge'] if 'edge' in kwargs else None
        self.traceback = kwargs['traceback'] if 'traceback' in kwargs else None


class DagExecError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.port = kwargs['port'] if 'port' in kwargs else None
        self.input = kwargs['input'] if 'input' in kwargs else None
        self.edge = kwargs['edge'] if 'edge' in kwargs else None
        self.traceback = kwargs['traceback'] if 'traceback' in kwargs else None
