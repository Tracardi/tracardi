from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from tracardi.domain.resource import Resource
from tracardi.domain.batch import Batch


class BatchRunner:

    def __init__(self, debug: bool, resource: Resource):
        self.credentials = resource.credentials.test if debug is True else resource.credentials.production
        self.config = None

    async def run(self, config):
        pass
